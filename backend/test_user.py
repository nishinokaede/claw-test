import bcrypt

# 测试密码哈希
def test_password():
    # 模拟创建用户时的哈希
    password = "admin123"
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    print(f"生成的哈希: {hashed.decode('utf-8')}")

    # 测试验证
    test_password = "admin123"
    test_bytes = test_password.encode('utf-8')[:72]
    result = bcrypt.checkpw(test_bytes, hashed)
    print(f"验证结果: {result}")

if __name__ == "__main__":
    test_password()
