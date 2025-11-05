graph TB

%% \===== L1: 用户界面 \=====  
subgraph L1\["用户层 (Human Interface Layer)"\]  
    UI\["Streamlit GUI V6\\n(指挥中心)"\]  
end

%% \===== L2: 应用核心层 \=====  
subgraph L2\["逻辑层 (Application Layer)"\]  
    API\["FastAPI Gateway\\nAuth / API / WebSocket"\]  
    ORC\["Orchestrator\\n任务编排器 (状态机核心)"\]  
    QUEUE\["Redis Queue\\n(任务流 \+ DLQ)"\]  
    DB\["PostgreSQL \+ pgvector\\n(状态库 \+ 向量索引)"\]  
    CBR\["CBR Module\\n(V4 经验库)"\]  
    OBJ\["对象存储 S3/MinIO\\n(计划/产物快照)"\]  
    OBS\["可观测性模块\\n(OTel / Grafana / Loki)"\]  
end

%% \===== L3: 智能 Agent 层 \=====  
subgraph L3\["智能层 (Cognitive Layer)"\]  
    P\["Perceptor Agent (V5)\\n环境感知/任务创建"\]  
    PL\["Planner Agent (V6)\\n检索+改编+规划"\]  
    W\["Writer Agent (V2)\\n执行 ToT 子图"\]  
    AD\["ArtDirector Agent (V3)\\n视觉自省"\]  
    TS\["ToolSmith Agent (V2)\\n动态代码/测试"\]  
    CR\["Critic Agent (V2)\\n评估与建议"\]  
    LLM\["LLM Proxy\\n(OpenAI / Claude / Gemini 路由层)"\]  
    SBX\["Sandbox 执行沙箱\\n(代码运行隔离)"\]  
end

%% \===== 外部 \=====  
EXT\["外部 API\\n(Google, OpenAI, Papers, News)"\]

%% \===== 连接关系 \=====  
UI \--\> API  
API \--\> ORC  
ORC \--\> QUEUE  
ORC \--\> DB  
ORC \--\> OBS  
ORC \--\> OBJ  
ORC \--\> CBR

QUEUE \--\> PL  
QUEUE \--\> W  
QUEUE \--\> AD  
QUEUE \--\> TS  
QUEUE \--\> CR  
QUEUE \--\> CBR

PL \--\> CBR  
PL \--\> DB  
PL \--\> LLM  
PL \--\> OBJ  
PL \--\> ORC

W \--\> SBX  
W \--\> LLM  
W \--\> OBJ  
W \--\> ORC

AD \--\> LLM  
AD \--\> ORC

TS \--\> SBX  
TS \--\> ORC

CR \--\> LLM  
CR \--\> ORC

P \--\> EXT  
P \--\> ORC

CBR \--\> DB  
CBR \--\> OBJ

LLM \--\> EXT

