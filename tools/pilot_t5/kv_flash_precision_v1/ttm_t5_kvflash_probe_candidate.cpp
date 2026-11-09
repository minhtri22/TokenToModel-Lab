// TTM T5 KV/Flash diagnostic candidate; DESIGN ONLY, no run permit.
// Must be built against pinned ggml-org/llama.cpp 372dc5ca157276beb6c67b2e92477e8d662e964a
// No TEST access, no checkpoint modification, new synthetic token IDs only.
// Owner preflight must verify exact GGUF SHA and gate before invocation.
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
#include <utility>
#include <vector>

namespace fs=std::filesystem;
struct Fixture { std::string name; std::vector<llama_token> ids; };
struct Arm { std::string name; ggml_type kv; llama_flash_attn_type flash; bool enabled; };
static const std::vector<Fixture> fixtures={
    {"SYN01", {470}},
    {"SYN02", {710, 1726}},
    {"SYN03", {950, 1846, 772, 1032}},
    {"SYN04", {1190, 1966, 732, 1023, 595, 1479}},
    {"SYN05", {1430, 938, 1335, 1014, 1963, 1788, 743, 493, 1718}},
    {"SYN06", {1670, 1058, 1938, 1648, 897, 1454, 1090, 491, 348, 1754, 1712, 1635}},
    {"SYN07", {1910, 1821, 1898, 1639, 474, 1763, 794, 1637, 1412, 881, 1156, 648, 840, 616, 716, 1084, 1041, 578, 909, 363}},
    {"SYN08", {359, 1941, 710, 1630, 1199, 1429, 1141, 992, 685, 1799, 600, 304, 923, 733, 1558, 956, 1680, 1130, 1019, 1394, 1662, 523, 493, 1580, 476, 276, 987, 1435, 742, 1289, 1945}},
};
static const Arm arms[]={
    {"S0", GGML_TYPE_F16, LLAMA_FLASH_ATTN_TYPE_ENABLED, true},
    {"S1", GGML_TYPE_F32, LLAMA_FLASH_ATTN_TYPE_DISABLED, false},
    {"S2", GGML_TYPE_F32, LLAMA_FLASH_ATTN_TYPE_ENABLED, true},
    {"S3", GGML_TYPE_F16, LLAMA_FLASH_ATTN_TYPE_DISABLED, false},
};
struct Counts { int flash_nodes=0; };
static bool trace_cb(ggml_tensor *t, bool ask, void *ud) {
    if (!t || !ud) return false;
    bool flash=(t->op==GGML_OP_FLASH_ATTN_EXT);
    if (ask) return flash;
    if (flash) static_cast<Counts*>(ud)->flash_nodes++;
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
    if (argc!=4) {
        std::cerr<<"usage: ttm_t5_kvflash_probe.exe <project_root> <pinned_gguf> <output.jsonl>\n";
        return 2;
    }
    llama_model *model=nullptr;
    bool backend_initialized=false;
    try {
        const fs::path root=fs::canonical(argv[1]);
        const fs::path gguf=fs::canonical(argv[2]);
        const fs::path out=fs::absolute(argv[3]);
        const fs::path parent=fs::canonical(out.parent_path());
        if(!is_under(root,gguf)||!is_under(root,parent)||fs::symlink_status(out).type()!=fs::file_type::not_found) throw std::runtime_error("PATH_SCOPE_OR_OUTPUT_EXISTS");
        if (fixtures.size()!=8) throw std::runtime_error("FIXTURE_COUNT");
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
        int rows=0;
        for(const auto& arm:arms){
            for(const auto& fixture:fixtures){
                Counts counts;
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
        if(!file||rows!=32)throw std::runtime_error("OUTPUT_ROW_COUNT_OR_FLUSH");
        file.close();
        llama_model_free(model);
        llama_backend_free();
        backend_initialized=false;
        std::cout<<"T5_NEW_SYNTHETIC_2X2_NATIVE_RUN=COMPLETE_ROWS_32\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr<<"T5_FAIL_CLOSED:"<<e.what()<<"\n";
        if(model)llama_model_free(model);
        if(backend_initialized)llama_backend_free();
        return 3;
    }
}
