from sqlalchmey.orm import Session
from database import get_db
from fastapi import APIRouter

app = APIRouter(
    prefix="/user"
)


@app.get("/test")
async def user_test():
    return "test"


@app.post(path="/signup") #회원가입
async def signup(new_user: user_schema.NewUserForm, db: Session  = Depends(get_db)):
    user = user_crud.get_user(new_user.id, db)

    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="사용자가 이미 존재합니다")
    user_crud.create_user(new_user, db)

    return HTTPException(status_code=status.HTTP_200_OK, detail="회원가입 성공")


@app.post(path="/login") #회원가입 후 로그인
async def login(login_form: OAuth2PasswordRequestForm = Depend(), db: Session = Depends(get_db)):
    user = user_crud.get_user(login_form.id, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 사용자 또는 비밀번호")   
    res = user_crud.verify_password(login_form.password, user.hashed_pw)


    if not res:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 사용자 또는 비밀번호")   
    return HTTPException(status_code=200, detail="로그인 성공")





    



