from pydantic import BaseModel, ConfigDict

# 회원가입 시 
class UserCreate(BaseModel):
    email: str
    name: str
    pwd: str

# 로그인 시
class UserLogin(BaseModel):
    memail: str
    mpw: str
    
# 응답 시
class UserOut(BaseModel):
    midx: int
    memail: str
    mname: str
    mstatus: int  
    model_config = ConfigDict(from_attributes=True)