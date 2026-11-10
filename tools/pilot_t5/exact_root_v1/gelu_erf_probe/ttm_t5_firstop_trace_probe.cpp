// TTM T5 first divergent op discovery D01/D02 only, source locked before execution.
// Must be built against pinned ggml-org/llama.cpp 372dc5ca157276beb6c67b2e92477e8d662e964a
// No TEST access, no checkpoint modification, new synthetic token IDs only.
// New 2-discovery fixtures only, no prior 8/32 fixture rerun, no TEST/train.
#include "llama.h"
#include "ggml.h"
#include "ggml-backend.h"
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <array>
#include <cstring>
#include <cstdint>
#include <memory>
#include <set>
#include <utility>
#include <vector>

namespace fs=std::filesystem;
struct Fixture { std::string name; std::vector<llama_token> ids; };
struct Arm { std::string name; ggml_type kv; llama_flash_attn_type flash; bool enabled; };
static const std::vector<Fixture> fixtures={
    {"D01", {1281}},
    {"D02", {1406, 971, 566, 1092, 1587}},
};
static const Arm arms[]={
    {"S1_F32_NO_FLASH", GGML_TYPE_F32, LLAMA_FLASH_ATTN_TYPE_DISABLED, false},
};
struct Trace {
    std::string fixture;
    std::ostream *sink=nullptr;
    int flash_nodes=0;
    std::set<std::string> captured;
    std::string failure;
};
static bool selected(const std::string &s) {
    static const std::set<std::string> wanted={
        "inpL","attn_norm-0","wqkv_b-0",
        "Qcur-0","Kcur-0","Vcur-0",
        "kq-0","kq_soft_max-0","kqv-0","kqv_out-0",
        "attn_wo_mm-0","attn_wo_out-0",
        "ffn_inp-0","ffn_norm-0","ffn_up_b-0",
        "ffn_gelu-0","ffn_gelu_erf-0","ffn_out-0","result_norm","result_output"
    };
    return wanted.count(s)!=0;
}
static bool trace_cb(ggml_tensor *t, bool ask, void *ud) {
    if(!t || !ud) return false;
    auto *state=static_cast<Trace*>(ud);
    const bool flash=(t->op==GGML_OP_FLASH_ATTN_EXT);
    const std::string name(t->name);
    // Only the genuine GELU_ERF graph node is canonicalized for comparison.
    // Retain the actual GGML node name independently for provenance.
    const std::string canonical_name = name=="ffn_gelu_erf-0" ? "ffn_gelu-0" : name;
    const bool wanted=selected(name);
    if(ask) return flash||wanted;
    if(flash) state->flash_nodes++;
    if(!wanted) return true;
    if(!state->failure.empty()) return false;
    // The selected graph nodes should be F32. Refuse silent F16 coercion.
    if(t->type!=GGML_TYPE_F32) {
        state->failure="NON_F32_CAPTURE:"+name;return false;
    }
    const size_t bytes=ggml_nbytes(t);
    const int64_t count=ggml_nelements(t);
    if(count<1 || count>262144 || bytes==0 || bytes>16*1024*1024) {
        state->failure="TENSOR_CAPTURE_TOO_LARGE:"+name;return false;
    }
    try {
        std::vector<unsigned char> blob(bytes);
        ggml_backend_tensor_get(t, blob.data(), 0, bytes);
        *state->sink << "{\"fixture_id\":\""<<state->fixture
                     <<"\",\"stage\":\""<<canonical_name<<"\",\"actual_node_name\":\""<<name<<"\",\"dtype\":\"F32\",\"ne\":[";
        for(int d=0;d<4;d++){if(d)*state->sink<<",";*state->sink<<t->ne[d];}
        *state->sink<<"],\"values\":[";
        size_t index=0;
        for(int64_t i3=0;i3<t->ne[3];i3++)
        for(int64_t i2=0;i2<t->ne[2];i2++)
        for(int64_t i1=0;i1<t->ne[1];i1++)
        for(int64_t i0=0;i0<t->ne[0];i0++){
            const size_t off=static_cast<size_t>(i0)*t->nb[0]
                +static_cast<size_t>(i1)*t->nb[1]
                +static_cast<size_t>(i2)*t->nb[2]
                +static_cast<size_t>(i3)*t->nb[3];
            if(off+sizeof(float)>blob.size()){
                state->failure="STRIDE_OUT_OF_BOUNDS:"+name;return false;
            }
            float value=0;std::memcpy(&value,blob.data()+off,sizeof(float));
            if(!std::isfinite(value)){
                state->failure="NONFINITE_TENSOR:"+name;return false;
            }
            if(index++)*state->sink<<",";
            *state->sink<<value;
        }
        *state->sink<<"]}\n";
        state->captured.insert(name);
        if(!*state->sink){
            state->failure="TRACE_FILE_IO_ERROR";return false;
        }
    }catch(const std::exception &e){
        state->failure="CAPTURE_EXCEPTION:"+name+":"+e.what();return false;
    }
    return true;
}
static bool is_under(const fs::path& root,const fs::path& child) {
    const fs::path rel=child.lexically_relative(root);
    if (rel.empty() || rel.is_absolute()) return false;
    for (const auto & part : rel) if (part=="..") return false;
    return rel!=fs::path(".");
}
static void emit_json_array(std::ostream &out,const std::vector<llama_token>& v) {
    out<<"[";
    for(size_t i=0;i<v.size();++i){if(i)out<<",";out<<v[i];}
    out<<"]";
}
int main(int argc, char **argv) {
    // This mode is safe to run in build QA: NO llama backend/model/inference.
    // It demonstrates the compiled constants and frozen fixture IDs.
    if (argc==2 && std::string(argv[1])=="--self-check") {
        if(fixtures.size()!=2 || (sizeof(arms)/sizeof(arms[0]))!=1) return 20;
        std::cout<<R"({"schema":"ttm.t5.firstop.discover_two.compiled_constants.v1","model_loaded":false,"native_inference":false,"fixtures":[)";
        for(size_t i=0;i<fixtures.size();++i){
            if(i)std::cout<<",";
            std::cout<<R"({"fixture_id":")"<<fixtures[i].name<<R"(","token_ids":)";
            emit_json_array(std::cout,fixtures[i].ids);
            std::cout<<"}";
        }
        std::cout<<R"(],"arms":[)";
        for(size_t i=0;i<(sizeof(arms)/sizeof(arms[0]));++i){
            if(i)std::cout<<",";
            std::cout<<R"({"id":")"<<arms[i].name<<R"(","kv":")"
                <<(arms[i].kv==GGML_TYPE_F16?"F16":"F32")<<R"(","flash":")"
                <<(arms[i].enabled?"ENABLED":"DISABLED")<<R"("})";
        }
        std::cout<<"]}\n";
        return 0;
    }
    if (argc!=4) {
        std::cerr<<"usage: ttm_t5_firstop_trace_probe.exe <project_root> <pinned_gguf> <output.jsonl>\n";
        return 2;
    }
    llama_model *model=nullptr;
    bool backend_initialized=false;
    try {
        const fs::path root=fs::canonical(argv[1]);
        const fs::path gguf=fs::canonical(argv[2]);
        const fs::path out=fs::absolute(argv[3]);
        const fs::path trace_out=fs::path(out.string()+".trace.jsonl");
        const fs::path parent=fs::canonical(out.parent_path());
        if(!is_under(root,gguf)||!is_under(root,parent)||fs::symlink_status(out).type()!=fs::file_type::not_found||fs::symlink_status(trace_out).type()!=fs::file_type::not_found) throw std::runtime_error("PATH_SCOPE_OR_OUTPUT_EXISTS");
        if (fixtures.size()!=2) throw std::runtime_error("FIXTURE_COUNT");
        llama_backend_init();
        backend_initialized=true;
        llama_model_params model_params=llama_model_default_params();
        model_params.n_gpu_layers=0;
        model=llama_model_load_from_file(gguf.string().c_str(),model_params);
        if(!model) throw std::runtime_error("MODEL_LOAD_FAILED");
        const llama_vocab *vocab=llama_model_get_vocab(model);
        if(!vocab||llama_vocab_n_tokens(vocab)!=2048)throw std::runtime_error("EXPECTED_VOCAB_2048");
        std::ofstream file(out,std::ios::out|std::ios::trunc);
        if(!file)throw std::runtime_error("OPEN_OUTPUT_FAILED");
        file<<std::setprecision(std::numeric_limits<float>::max_digits10);
        std::ofstream trace_file(trace_out,std::ios::out|std::ios::trunc);
        if(!trace_file)throw std::runtime_error("TRACE_OPEN_FAILED");
        trace_file<<std::setprecision(std::numeric_limits<float>::max_digits10);
        int rows=0;
        for(const auto& arm:arms){
            for(const auto& fixture:fixtures){
                Trace counts{fixture.name,&trace_file};
                llama_context_params ctx_params=llama_context_default_params();
                ctx_params.n_ctx=256;
                ctx_params.n_batch=256;
                ctx_params.n_ubatch=256;
                ctx_params.n_seq_max=1;
                ctx_params.n_threads=1;
                ctx_params.n_threads_batch=1;
                ctx_params.offload_kqv=false;
                ctx_params.op_offload=false;
                ctx_params.type_k=arm.kv;
                ctx_params.type_v=arm.kv;
                ctx_params.flash_attn_type=arm.flash;
                ctx_params.cb_eval=trace_cb;
                ctx_params.cb_eval_user_data=&counts;
                llama_context *ctx=llama_init_from_model(model,ctx_params);
                if(!ctx)throw std::runtime_error("CONTEXT_INIT_FAILED:"+arm.name);
                llama_batch batch=llama_batch_init(static_cast<int32_t>(fixture.ids.size()),0,1);
                batch.n_tokens=static_cast<int32_t>(fixture.ids.size());
                for(int i=0;i<batch.n_tokens;i++){
                    batch.token[i]=fixture.ids.at(static_cast<size_t>(i));
                    batch.pos[i]=i;
                    batch.n_seq_id[i]=1;
                    batch.seq_id[i][0]=0;
                    batch.logits[i]=i==batch.n_tokens-1;
                }
                const int rc=llama_decode(ctx,batch);
                if(rc!=0){llama_batch_free(batch);llama_free(ctx);throw std::runtime_error("DECODE_FAILED:"+arm.name+":"+fixture.name);}
                if(!counts.failure.empty()){llama_batch_free(batch);llama_free(ctx);throw std::runtime_error(counts.failure);}
                for(const auto &required: std::array<const char*,10>{"inpL","attn_norm-0","wqkv_b-0","kqv-0","attn_wo_mm-0","attn_wo_out-0","ffn_inp-0","ffn_up_b-0","ffn_gelu_erf-0","result_output"}){
                    if(counts.captured.count(required)==0){llama_batch_free(batch);llama_free(ctx);throw std::runtime_error(std::string("REQUIRED_TRACE_STAGE_MISSING:")+required);}
                }
                float *logits=llama_get_logits_ith(ctx,-1);
                if(!logits){llama_batch_free(batch);llama_free(ctx);throw std::runtime_error("NO_LOGITS");}
                if((arm.enabled && counts.flash_nodes==0)||(!arm.enabled && counts.flash_nodes!=0)){
                    llama_batch_free(batch);llama_free(ctx);
                    throw std::runtime_error("FLASH_RUNTIME_PATH_MISMATCH:"+arm.name+":"+fixture.name);
                }
                // Each record is self-contained: all 2048 F32 logits and the exact configuration.
                file<<"{\"fixture_id\":\""<<fixture.name<<"\",\"arm_id\":\""<<arm.name
                    <<"\",\"kv_type\":\""<<(arm.kv==GGML_TYPE_F16?"F16":"F32")
                    <<"\",\"flash\":\""<<(arm.enabled?"ENABLED":"DISABLED")
                    <<"\",\"flash_nodes_observed\":"<<counts.flash_nodes
                    <<",\"token_ids\":";
                emit_json_array(file,fixture.ids);
                file<<",\"logits\":[";
                for(int j=0;j<2048;j++){
                    if(!std::isfinite(logits[j])){llama_batch_free(batch);llama_free(ctx);throw std::runtime_error("NONFINITE_LOGIT");}
                    if(j)file<<",";
                    file<<logits[j];
                }
                file<<"]}\n";
                llama_batch_free(batch);
                llama_free(ctx);
                rows++;
            }
        }
        file.flush();
        if(!file||!trace_file||rows!=2)throw std::runtime_error("OUTPUT_ROW_COUNT_OR_FLUSH");
        file.close();
        trace_file.flush();if(!trace_file)throw std::runtime_error("TRACE_FLUSH_FAILED");trace_file.close();
        llama_model_free(model);
        llama_backend_free();
        backend_initialized=false;
        std::cout<<"T5_FIRST_OP_DISCOVERY_COMPLETE_ROWS_2\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr<<"T5_FAIL_CLOSED:"<<e.what()<<"\n";
        if(model)llama_model_free(model);
        if(backend_initialized)llama_backend_free();
        return 3;
    }
}
