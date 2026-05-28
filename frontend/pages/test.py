data = {
    "code": 200,
    "msg": "启用成功",
    "data": {
        "id": 2,
        "phone": "13810114001",
        "password": "$2b$12$W5OAIrg5lf1VZDku2rrsmebuN/UhWW7vIHgi5S/k1xD91wY7P/nNu",
        "name": "测试用户",
        "school": "测试学校",
        "title": "老师",
        "role": "user",
        "status": 1,
        "create_time": "2026-05-13T16:01:16",
        "update_time": "2026-05-13T16:01:16"
    }

}

users = data["user"]


users["id"] = f"ID:{users['id']}"
users["phone"] = f"手机号:{users['phone']}"
users["name"] = f"姓名:{users['name']}"
users["school"] = f"学校:{users['school']}"
users["title"] = f"职称:{users['title']}"
users["role"] = f"角色:{users['role']}"
users["status"] = f"状态: {'正常' if users['status'] == 1 else '禁用'}"
users["create_time"] = f"注册时间:{users['create_time']}"

print(users)

