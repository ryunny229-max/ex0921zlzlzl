from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import get_db
from models.memo import Memo
from schemas.memo import MemoCreate, MemoUpdate, MemoOut
from typing import List

# 예)  himedia.co.kr/memos/add, .../memos/total, .../memos/update 
router = APIRouter(prefix="/memos", tags=["memos"])

@router.post("/add", response_model=MemoOut)
async def create_memo(payload: MemoCreate, db: AsyncSession = Depends(get_db)):
    memo = Memo(
        title=payload.title,
        content=payload.content
    )
    db.add(memo)   # 동기메서드
    await db.commit()  # 비동기 I/O 이기 때문에 await필수
    await db.refresh(memo) # DB에서 idx와 create_at 등을 다시 읽어옴 
    return memo

@router.get("/list", response_model=List[MemoOut])
async def list_memo(db: AsyncSession = Depends(get_db)):
    # SqlAlchemy 2.0의 스타일
    stmt = select(Memo).order_by(Memo.idx)
    result = await db.execute(stmt) # Result객체를 먼저 얻고
    list = result.scalars().all() # 스칼라 활성
    return list

@router.put("/edit", response_model=MemoOut)
async def edit_memo(idx:int, payload:MemoUpdate, db: AsyncSession = Depends(get_db)):
    # idx로 검색
    memo = await db.get(Memo, idx)
    # 위의 memo가 있을 때만 수정기능을 수행해야 한다.
    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memo not found"
        )
        
    # 컬럼 값 수정
    if payload.title is not None: # 인자로 넘어온 title이 비어있지 않다면
        memo.title = payload.title # ORM모델의 title을 인자값 title로 변경
    if payload.content is not None:
        memo.content = payload.content
        
    # 트랜잭션 커밋 및 갱신 비동기 대기
    await db.commit()
    await db.refresh(memo)    
    return memo

@router.delete("/delete")
async def delete_memo(idx: int, db: AsyncSession = Depends(get_db)):
    # 인자로 받은 idx값으로 먼저 검색하여 검색된 결과가 있으면 삭제하면 된다.
    memo = await db.get(Memo, idx)
    if memo is None:
        raise HTTPException(status_code=404, detail="Memo not found")
    
    await db.delete(memo)
    await db.commit()
    return None