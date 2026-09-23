import time, uuid
from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass(frozen=True) # makes instances read only
class InferenceRequest:
    prompt_tokens:   list[int]
    max_new_tokens:  int
    request_id:      str        = field(default_factory=lambda: str(uuid.uuid4())) # to get new UUID's per request
    temperature:     float      = 1.0
    top_p:           float      = 1.0
    stream:          bool       = False
    seq_len_bucket:  str        = 'medium'
    enqueue_ts:      float      = field(default_factory=time.time)
    client_id:       str        = 'anonymous'

    def to_json(self) -> bytes:
        import dataclasses
        return json.dumps(dataclasses.asdict(self)).encode()

    @classmethod
    def from_json(cls, data: bytes) -> 'InferenceRequest':
        return cls(**json.loads(data))

@dataclass
class InferenceResponse:
    request_id:       str
    status:           str
    output_tokens:    list[int]    = field(default_factory=list)
    output_text:      str          = ''
    token_count:      int          = 0
    ttft_ms:          float        = 0.0
    total_latency_ms: float        = 0.0
    batch_id:         str          = ''
    error_msg:        Optional[str]= None
    worker_id:        str          = ''