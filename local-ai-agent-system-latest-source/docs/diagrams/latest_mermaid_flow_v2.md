# Latest Mermaid Flow v2

```mermaid
flowchart TD
    ER["External Request"] --> FG["OpenClaw Gateway"]
    FG --> MAIN["AI-Artist Main Agent"]
    MAIN --> FSS["FastAPI Safety Service"]
    FSS --> RC["Request Canonicalizer"]
    RC --> PCB["Policy Context Builder"]
    PCB --> OPA["OPA Policy Layer"]
    OPA --> RCL{"Request Classifier"}

    RCL -->|"repeat read query"| RG["Reuse Gate"]
    RG --> SFC["Source Freshness Check"]
    SFC -->|"approved + unchanged"| ARC["Approved Response Cache"]
    SFC -->|"miss / changed"| FA["OpenClaw Main Agent"]
    ARC --> FVAL["Final Validation"]

    RCL -->|"fresh query or action"| FA
    FA --> HO["OpenClaw Agent Runtime"]
    HO --> SUB["Restricted OpenClaw Sub-Agents"]
    SUB --> TESTS["Task Validation Tests"]
    TESTS --> SYN["Validation / Compare / Retry / Synthesis"]
    SYN --> FVAL
    FVAL --> FRA["Final Response / Action"]
    FRA --> EPG["Execution Policy Gate"]
    EPG --> OTA["Output Tool Agent"]
    OTA --> CH["Channels / Platforms"]
```
