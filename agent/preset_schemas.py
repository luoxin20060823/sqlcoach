"""4 个内置示例数据库 — 开箱即用，0 等待

这些 schema 与 4 个 DOMAINS 一一对应，体积适中（每表 8~15 行），
字段覆盖了 SELECT / JOIN / GROUP BY / 子查询 / 窗口函数 等常见考点。
"""

PRESET_SCHEMAS = {
    "学生管理系统": """
-- 学生管理系统：班级、学生、课程、选课成绩
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY,
    class_name TEXT NOT NULL,
    grade INTEGER NOT NULL,
    head_teacher TEXT
);

CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    class_id INTEGER,
    enroll_date TEXT,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY,
    course_name TEXT NOT NULL,
    credit INTEGER,
    teacher TEXT
);

CREATE TABLE enrollments (
    student_id INTEGER,
    course_id INTEGER,
    score REAL,
    semester TEXT,
    PRIMARY KEY (student_id, course_id, semester),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

INSERT INTO classes VALUES (1, '一班', 2024, '李老师');
INSERT INTO classes VALUES (2, '二班', 2024, '王老师');
INSERT INTO classes VALUES (3, '三班', 2023, '张老师');
INSERT INTO classes VALUES (4, '四班', 2023, '赵老师');

INSERT INTO students VALUES (1001, '张明',  '男', 19, 1, '2024-09-01');
INSERT INTO students VALUES (1002, '李华',  '女', 20, 1, '2024-09-01');
INSERT INTO students VALUES (1003, '王芳',  '女', 19, 2, '2024-09-01');
INSERT INTO students VALUES (1004, '刘强',  '男', 21, 2, '2024-09-01');
INSERT INTO students VALUES (1005, '陈静',  '女', 20, 3, '2023-09-01');
INSERT INTO students VALUES (1006, '杨阳',  '男', 22, 3, '2023-09-01');
INSERT INTO students VALUES (1007, '周丽',  '女', 21, 4, '2023-09-01');
INSERT INTO students VALUES (1008, '吴磊',  '男', 19, 4, '2023-09-01');
INSERT INTO students VALUES (1009, '黄薇',  '女', 20, 1, '2024-09-01');
INSERT INTO students VALUES (1010, '徐峰',  '男', NULL, 2, '2024-09-01');

INSERT INTO courses VALUES (101, '高等数学',   4, '钱教授');
INSERT INTO courses VALUES (102, '数据结构',   3, '孙教授');
INSERT INTO courses VALUES (103, '数据库原理', 3, '周教授');
INSERT INTO courses VALUES (104, '英语',       2, '吴教授');
INSERT INTO courses VALUES (105, '操作系统',   3, '郑教授');

INSERT INTO enrollments VALUES (1001, 101, 88, '2024-秋');
INSERT INTO enrollments VALUES (1001, 102, 76, '2024-秋');
INSERT INTO enrollments VALUES (1001, 103, 92, '2024-秋');
INSERT INTO enrollments VALUES (1002, 101, 95, '2024-秋');
INSERT INTO enrollments VALUES (1002, 103, 89, '2024-秋');
INSERT INTO enrollments VALUES (1003, 101, 67, '2024-秋');
INSERT INTO enrollments VALUES (1003, 102, 82, '2024-秋');
INSERT INTO enrollments VALUES (1003, 104, 91, '2024-秋');
INSERT INTO enrollments VALUES (1004, 102, 55, '2024-秋');
INSERT INTO enrollments VALUES (1004, 105, 71, '2024-秋');
INSERT INTO enrollments VALUES (1005, 101, 78, '2024-秋');
INSERT INTO enrollments VALUES (1005, 103, 85, '2024-秋');
INSERT INTO enrollments VALUES (1006, 102, 90, '2024-秋');
INSERT INTO enrollments VALUES (1006, 105, 88, '2024-秋');
INSERT INTO enrollments VALUES (1007, 104, 99, '2024-秋');
INSERT INTO enrollments VALUES (1008, 101, NULL, '2024-秋');
INSERT INTO enrollments VALUES (1008, 103, 70, '2024-秋');
INSERT INTO enrollments VALUES (1009, 102, 84, '2024-秋');
INSERT INTO enrollments VALUES (1010, 105, 60, '2024-秋');
""".strip(),

    "电商订单系统": """
-- 电商订单系统：用户、商品、订单、订单明细
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    city TEXT,
    register_date TEXT,
    vip_level INTEGER DEFAULT 0
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL,
    stock INTEGER
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    order_date TEXT,
    status TEXT,
    total_amount REAL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO users VALUES (1, '张三', '北京', '2023-01-15', 2);
INSERT INTO users VALUES (2, '李四', '上海', '2023-03-20', 1);
INSERT INTO users VALUES (3, '王五', '广州', '2023-05-10', 3);
INSERT INTO users VALUES (4, '赵六', '深圳', '2024-01-05', 0);
INSERT INTO users VALUES (5, '钱七', '杭州', '2024-02-18', 2);
INSERT INTO users VALUES (6, '孙八', '成都', '2024-06-22', 1);
INSERT INTO users VALUES (7, '周九', '北京', '2024-07-30', 0);
INSERT INTO users VALUES (8, '吴十', '武汉', NULL,         0);

INSERT INTO products VALUES (101, '无线鼠标',     '电子',  99.0,  150);
INSERT INTO products VALUES (102, '机械键盘',     '电子',  399.0, 80);
INSERT INTO products VALUES (103, '27寸显示器',   '电子',  1599.0,30);
INSERT INTO products VALUES (104, 'T恤',          '服装',  89.0,  500);
INSERT INTO products VALUES (105, '牛仔裤',       '服装',  199.0, 200);
INSERT INTO products VALUES (106, '保温杯',       '日用',  59.0,  300);
INSERT INTO products VALUES (107, '蓝牙耳机',     '电子',  299.0, 120);
INSERT INTO products VALUES (108, '运动鞋',       '服装',  499.0, 90);

INSERT INTO orders VALUES (1001, 1, '2024-03-01', 'paid',     498.0);
INSERT INTO orders VALUES (1002, 1, '2024-04-12', 'paid',     1599.0);
INSERT INTO orders VALUES (1003, 2, '2024-04-20', 'shipped',  189.0);
INSERT INTO orders VALUES (1004, 3, '2024-05-05', 'paid',     897.0);
INSERT INTO orders VALUES (1005, 3, '2024-06-18', 'cancelled',299.0);
INSERT INTO orders VALUES (1006, 4, '2024-07-01', 'paid',     59.0);
INSERT INTO orders VALUES (1007, 5, '2024-08-09', 'paid',     698.0);
INSERT INTO orders VALUES (1008, 5, '2024-09-15', 'shipped',  399.0);
INSERT INTO orders VALUES (1009, 6, '2024-10-20', 'paid',     1098.0);
INSERT INTO orders VALUES (1010, 7, '2024-11-11', 'paid',     297.0);
INSERT INTO orders VALUES (1011, 1, '2024-12-01', 'paid',     888.0);
INSERT INTO orders VALUES (1012, 3, '2024-12-25', 'paid',     499.0);

INSERT INTO order_items VALUES (1, 1001, 101, 2, 99.0);
INSERT INTO order_items VALUES (2, 1001, 107, 1, 299.0);
INSERT INTO order_items VALUES (3, 1002, 103, 1, 1599.0);
INSERT INTO order_items VALUES (4, 1003, 104, 1, 89.0);
INSERT INTO order_items VALUES (5, 1003, 106, 1, 59.0);
INSERT INTO order_items VALUES (6, 1004, 102, 1, 399.0);
INSERT INTO order_items VALUES (7, 1004, 108, 1, 499.0);
INSERT INTO order_items VALUES (8, 1005, 107, 1, 299.0);
INSERT INTO order_items VALUES (9, 1006, 106, 1, 59.0);
INSERT INTO order_items VALUES (10, 1007, 102, 1, 399.0);
INSERT INTO order_items VALUES (11, 1007, 107, 1, 299.0);
INSERT INTO order_items VALUES (12, 1008, 102, 1, 399.0);
INSERT INTO order_items VALUES (13, 1009, 103, 1, 1599.0);   -- 单价改了
INSERT INTO order_items VALUES (14, 1010, 101, 3, 99.0);
INSERT INTO order_items VALUES (15, 1011, 108, 1, 499.0);
INSERT INTO order_items VALUES (16, 1011, 105, 1, 199.0);
INSERT INTO order_items VALUES (17, 1011, 102, 1, 199.0);
INSERT INTO order_items VALUES (18, 1012, 108, 1, 499.0);
""".strip(),

    "图书管理系统": """
-- 图书管理系统：读者、图书、作者、借阅记录
CREATE TABLE readers (
    reader_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    reader_type TEXT,    -- student / teacher / public
    register_date TEXT
);

CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    author_name TEXT NOT NULL,
    nationality TEXT
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INTEGER,
    category TEXT,
    publish_year INTEGER,
    total_copies INTEGER,
    available_copies INTEGER,
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);

CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY,
    reader_id INTEGER,
    book_id INTEGER,
    borrow_date TEXT,
    return_date TEXT,    -- NULL 表示尚未归还
    FOREIGN KEY (reader_id) REFERENCES readers(reader_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

INSERT INTO readers VALUES (1, '张三', 'student', '2023-09-01');
INSERT INTO readers VALUES (2, '李四', 'student', '2023-09-01');
INSERT INTO readers VALUES (3, '王五', 'teacher', '2020-03-15');
INSERT INTO readers VALUES (4, '赵六', 'teacher', '2018-09-01');
INSERT INTO readers VALUES (5, '钱七', 'public',  '2024-01-10');
INSERT INTO readers VALUES (6, '孙八', 'student', '2024-09-01');
INSERT INTO readers VALUES (7, '周九', 'public',  '2024-05-20');

INSERT INTO authors VALUES (1, '鲁迅',     '中国');
INSERT INTO authors VALUES (2, '老舍',     '中国');
INSERT INTO authors VALUES (3, '海明威',   '美国');
INSERT INTO authors VALUES (4, '村上春树', '日本');
INSERT INTO authors VALUES (5, '钱钟书',   '中国');
INSERT INTO authors VALUES (6, '马尔克斯', '哥伦比亚');

INSERT INTO books VALUES (101, '呐喊',           1, '小说', 1923, 5, 3);
INSERT INTO books VALUES (102, '彷徨',           1, '小说', 1926, 3, 1);
INSERT INTO books VALUES (103, '骆驼祥子',       2, '小说', 1939, 4, 2);
INSERT INTO books VALUES (104, '茶馆',           2, '戏剧', 1957, 2, 2);
INSERT INTO books VALUES (105, '老人与海',       3, '小说', 1952, 6, 4);
INSERT INTO books VALUES (106, '挪威的森林',     4, '小说', 1987, 5, 0);
INSERT INTO books VALUES (107, '1Q84',           4, '小说', 2009, 4, 2);
INSERT INTO books VALUES (108, '围城',           5, '小说', 1947, 3, 1);
INSERT INTO books VALUES (109, '百年孤独',       6, '小说', 1967, 5, 3);
INSERT INTO books VALUES (110, '霍乱时期的爱情', 6, '小说', 1985, 2, 1);

INSERT INTO loans VALUES (1, 1, 101, '2024-10-01', '2024-10-20');
INSERT INTO loans VALUES (2, 1, 105, '2024-11-05', NULL);
INSERT INTO loans VALUES (3, 2, 102, '2024-09-15', '2024-10-10');
INSERT INTO loans VALUES (4, 2, 108, '2024-11-20', NULL);
INSERT INTO loans VALUES (5, 3, 109, '2024-08-01', '2024-09-15');
INSERT INTO loans VALUES (6, 3, 106, '2024-10-10', NULL);
INSERT INTO loans VALUES (7, 4, 107, '2024-07-20', '2024-08-30');
INSERT INTO loans VALUES (8, 4, 110, '2024-09-01', '2024-10-05');
INSERT INTO loans VALUES (9, 5, 105, '2024-10-25', NULL);
INSERT INTO loans VALUES (10, 6, 103, '2024-11-01', NULL);
INSERT INTO loans VALUES (11, 7, 106, '2024-11-15', NULL);
INSERT INTO loans VALUES (12, 1, 109, '2024-06-10', '2024-07-01');
""".strip(),

    "企业人事系统": """
-- 企业人事系统：部门、员工、薪资、考勤
CREATE TABLE departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL,
    location TEXT,
    manager_id INTEGER  -- 自引用 employees.emp_id
);

CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    hire_date TEXT,
    dept_id INTEGER,
    position TEXT,
    base_salary REAL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

CREATE TABLE salaries (
    record_id INTEGER PRIMARY KEY,
    emp_id INTEGER,
    pay_month TEXT,        -- YYYY-MM
    base REAL,
    bonus REAL,
    deduction REAL,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

CREATE TABLE attendances (
    att_id INTEGER PRIMARY KEY,
    emp_id INTEGER,
    att_date TEXT,
    status TEXT,           -- present / absent / late / leave
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

INSERT INTO departments VALUES (1, '技术部',   '北京', 1001);
INSERT INTO departments VALUES (2, '销售部',   '上海', 1005);
INSERT INTO departments VALUES (3, '人事部',   '北京', 1009);
INSERT INTO departments VALUES (4, '财务部',   '北京', NULL);

INSERT INTO employees VALUES (1001, '张总监', '男', '2018-03-01', 1, '总监',   30000);
INSERT INTO employees VALUES (1002, '李工',   '男', '2020-07-15', 1, '高级',   18000);
INSERT INTO employees VALUES (1003, '王工',   '女', '2021-09-20', 1, '中级',   12000);
INSERT INTO employees VALUES (1004, '赵工',   '男', '2023-04-10', 1, '初级',    8000);
INSERT INTO employees VALUES (1005, '钱经理', '女', '2017-08-01', 2, '经理',   25000);
INSERT INTO employees VALUES (1006, '孙销售', '男', '2022-02-15', 2, '专员',    9000);
INSERT INTO employees VALUES (1007, '周销售', '女', '2023-06-20', 2, '专员',    9000);
INSERT INTO employees VALUES (1008, '吴销售', '男', '2024-01-10', 2, '助理',    6000);
INSERT INTO employees VALUES (1009, '郑主管', '女', '2019-05-01', 3, '主管',   18000);
INSERT INTO employees VALUES (1010, '冯专员', '女', '2023-09-01', 3, '专员',    8500);
INSERT INTO employees VALUES (1011, '陈会计', '男', '2020-03-15', 4, '主办',   13000);

INSERT INTO salaries VALUES (1, 1001, '2024-10', 30000, 5000,  0);
INSERT INTO salaries VALUES (2, 1001, '2024-11', 30000, 8000,  0);
INSERT INTO salaries VALUES (3, 1002, '2024-10', 18000, 2000,  500);
INSERT INTO salaries VALUES (4, 1002, '2024-11', 18000, 3000,  0);
INSERT INTO salaries VALUES (5, 1003, '2024-10', 12000, 1500,  0);
INSERT INTO salaries VALUES (6, 1003, '2024-11', 12000, 2000,  300);
INSERT INTO salaries VALUES (7, 1004, '2024-10',  8000, 500,   0);
INSERT INTO salaries VALUES (8, 1004, '2024-11',  8000, 800,   0);
INSERT INTO salaries VALUES (9, 1005, '2024-10', 25000, 6000,  0);
INSERT INTO salaries VALUES (10,1005, '2024-11', 25000, 9000,  0);
INSERT INTO salaries VALUES (11,1006, '2024-10',  9000, 3000,  0);
INSERT INTO salaries VALUES (12,1006, '2024-11',  9000, 4500,  200);
INSERT INTO salaries VALUES (13,1009, '2024-11', 18000, 2500,  0);
INSERT INTO salaries VALUES (14,1011, '2024-11', 13000, 1500,  0);

INSERT INTO attendances VALUES (1, 1002, '2024-11-01', 'present');
INSERT INTO attendances VALUES (2, 1002, '2024-11-04', 'late');
INSERT INTO attendances VALUES (3, 1003, '2024-11-01', 'present');
INSERT INTO attendances VALUES (4, 1003, '2024-11-05', 'absent');
INSERT INTO attendances VALUES (5, 1004, '2024-11-01', 'present');
INSERT INTO attendances VALUES (6, 1006, '2024-11-01', 'leave');
INSERT INTO attendances VALUES (7, 1007, '2024-11-01', 'present');
INSERT INTO attendances VALUES (8, 1010, '2024-11-01', 'late');
""".strip(),

    "医院挂号系统": """
-- 医院挂号系统：科室、医生、病人、挂号记录
CREATE TABLE departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT NOT NULL,
    location TEXT
);

CREATE TABLE doctors (
    doctor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT,        -- 主任 / 副主任 / 主治 / 住院
    dept_id INTEGER,
    consult_fee REAL,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

CREATE TABLE patients (
    patient_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    phone TEXT
);

CREATE TABLE appointments (
    appointment_id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    appoint_date TEXT,
    status TEXT,         -- booked / done / cancelled / no_show
    fee_paid REAL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

INSERT INTO departments VALUES (1, '内科',   '门诊楼 2 层');
INSERT INTO departments VALUES (2, '外科',   '门诊楼 3 层');
INSERT INTO departments VALUES (3, '儿科',   '门诊楼 1 层');
INSERT INTO departments VALUES (4, '皮肤科', '门诊楼 4 层');
INSERT INTO departments VALUES (5, '中医科', '门诊楼 5 层');

INSERT INTO doctors VALUES (1, '林主任', '主任',   1, 100);
INSERT INTO doctors VALUES (2, '王副主任','副主任',1, 60);
INSERT INTO doctors VALUES (3, '张医生', '主治',   1, 30);
INSERT INTO doctors VALUES (4, '陈主任', '主任',   2, 100);
INSERT INTO doctors VALUES (5, '刘医生', '主治',   2, 30);
INSERT INTO doctors VALUES (6, '赵医生', '住院',   3, 20);
INSERT INTO doctors VALUES (7, '钱主任', '主任',   3, 100);
INSERT INTO doctors VALUES (8, '孙副主任','副主任',4, 60);
INSERT INTO doctors VALUES (9, '李医生', '主治',   5, 40);
INSERT INTO doctors VALUES (10,'周医生', '住院',   5, NULL);

INSERT INTO patients VALUES (1, '老王', '男', 55, '139xxxx0001');
INSERT INTO patients VALUES (2, '小李', '女', 28, '139xxxx0002');
INSERT INTO patients VALUES (3, '小红', '女',  6, '139xxxx0003');
INSERT INTO patients VALUES (4, '老张', '男', 70, '139xxxx0004');
INSERT INTO patients VALUES (5, '小明', '男', 32, '139xxxx0005');
INSERT INTO patients VALUES (6, '小芳', '女', 41, NULL);

INSERT INTO appointments VALUES (1, 1, 1, '2024-11-01', 'done',      100);
INSERT INTO appointments VALUES (2, 1, 3, '2024-11-15', 'done',      30);
INSERT INTO appointments VALUES (3, 2, 4, '2024-11-02', 'done',      100);
INSERT INTO appointments VALUES (4, 2, 8, '2024-11-20', 'cancelled', 0);
INSERT INTO appointments VALUES (5, 3, 7, '2024-11-03', 'done',      100);
INSERT INTO appointments VALUES (6, 3, 6, '2024-11-25', 'booked',    20);
INSERT INTO appointments VALUES (7, 4, 1, '2024-11-04', 'done',      100);
INSERT INTO appointments VALUES (8, 4, 9, '2024-11-12', 'no_show',   0);
INSERT INTO appointments VALUES (9, 5, 2, '2024-11-05', 'done',      60);
INSERT INTO appointments VALUES (10, 5, 5, '2024-11-22', 'booked',   30);
INSERT INTO appointments VALUES (11, 6, 8, '2024-11-08', 'done',     60);
INSERT INTO appointments VALUES (12, 6, 1, '2024-11-30', 'booked',   100);
""".strip(),

    "银行交易系统": """
-- 银行交易系统：客户、账户、交易、网点
CREATE TABLE branches (
    branch_id INTEGER PRIMARY KEY,
    branch_name TEXT NOT NULL,
    city TEXT
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    register_branch INTEGER,
    FOREIGN KEY (register_branch) REFERENCES branches(branch_id)
);

CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    account_type TEXT,    -- saving / checking / credit
    balance REAL,
    open_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE transactions (
    txn_id INTEGER PRIMARY KEY,
    account_id INTEGER,
    txn_type TEXT,        -- deposit / withdraw / transfer / consume
    amount REAL,
    txn_time TEXT,
    counterpart TEXT,     -- 对手账户/商户名（可空）
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

INSERT INTO branches VALUES (1, '北京中关村支行', '北京');
INSERT INTO branches VALUES (2, '北京国贸支行',   '北京');
INSERT INTO branches VALUES (3, '上海浦东支行',   '上海');
INSERT INTO branches VALUES (4, '深圳南山支行',   '深圳');

INSERT INTO customers VALUES (1, '张三', 35, 1);
INSERT INTO customers VALUES (2, '李四', 28, 1);
INSERT INTO customers VALUES (3, '王五', 50, 2);
INSERT INTO customers VALUES (4, '赵六', 24, 3);
INSERT INTO customers VALUES (5, '钱七', 45, 3);
INSERT INTO customers VALUES (6, '孙八', NULL, 4);
INSERT INTO customers VALUES (7, '周九', 32, 4);

INSERT INTO accounts VALUES (1001, 1, 'saving',   25800,   '2020-03-15');
INSERT INTO accounts VALUES (1002, 1, 'credit',   -3200,   '2022-01-10');
INSERT INTO accounts VALUES (1003, 2, 'saving',   12500,   '2021-08-20');
INSERT INTO accounts VALUES (1004, 3, 'saving',   189000,  '2018-05-01');
INSERT INTO accounts VALUES (1005, 3, 'checking', 7500,    '2019-09-10');
INSERT INTO accounts VALUES (1006, 4, 'saving',   3800,    '2024-02-15');
INSERT INTO accounts VALUES (1007, 5, 'saving',   65000,   '2017-11-01');
INSERT INTO accounts VALUES (1008, 5, 'credit',   -8800,   '2021-04-12');
INSERT INTO accounts VALUES (1009, 6, 'saving',   42000,   '2020-07-20');
INSERT INTO accounts VALUES (1010, 7, 'checking', 15600,   '2023-01-05');

INSERT INTO transactions VALUES (1, 1001, 'deposit',  3000, '2024-10-01 09:30', NULL);
INSERT INTO transactions VALUES (2, 1001, 'withdraw', 800,  '2024-10-05 14:00', NULL);
INSERT INTO transactions VALUES (3, 1002, 'consume',  500,  '2024-10-08 12:15', '美团外卖');
INSERT INTO transactions VALUES (4, 1002, 'consume',  2700, '2024-10-15 19:45', '京东商城');
INSERT INTO transactions VALUES (5, 1003, 'transfer', 1500, '2024-10-10 10:00', '账户1004');
INSERT INTO transactions VALUES (6, 1004, 'deposit',  20000,'2024-10-12 11:00', NULL);
INSERT INTO transactions VALUES (7, 1004, 'transfer', 5000, '2024-10-20 16:30', '账户1007');
INSERT INTO transactions VALUES (8, 1005, 'withdraw', 1200, '2024-10-22 15:00', NULL);
INSERT INTO transactions VALUES (9, 1007, 'deposit',  5000, '2024-10-20 16:30', '账户1004转入');
INSERT INTO transactions VALUES (10,1008, 'consume',  3500, '2024-10-25 21:00', '苹果旗舰店');
INSERT INTO transactions VALUES (11,1009, 'withdraw', 8000, '2024-10-28 10:30', NULL);
INSERT INTO transactions VALUES (12,1010, 'deposit',  6000, '2024-11-01 09:00', NULL);
INSERT INTO transactions VALUES (13,1010, 'consume',  450,  '2024-11-05 18:30', '星巴克');
INSERT INTO transactions VALUES (14,1003, 'consume',  280,  '2024-11-08 13:00', '盒马生鲜');
""".strip(),

    "餐厅外卖系统": """
-- 餐厅外卖系统：餐厅、菜品、客户、订单、订单明细
CREATE TABLE restaurants (
    restaurant_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cuisine TEXT,        -- 川菜 / 粤菜 / 西餐 / 日料
    rating REAL,
    city TEXT
);

CREATE TABLE dishes (
    dish_id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    dish_name TEXT NOT NULL,
    price REAL,
    is_signature INTEGER DEFAULT 0,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    restaurant_id INTEGER,
    order_time TEXT,
    status TEXT,         -- delivered / cancelled / pending
    delivery_fee REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    dish_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
);

INSERT INTO restaurants VALUES (1, '蜀香居',     '川菜', 4.6, '北京');
INSERT INTO restaurants VALUES (2, '广粤楼',     '粤菜', 4.8, '北京');
INSERT INTO restaurants VALUES (3, '寿司道',     '日料', 4.5, '上海');
INSERT INTO restaurants VALUES (4, '帕斯塔咖啡', '西餐', 4.3, '上海');
INSERT INTO restaurants VALUES (5, '麻辣烫小馆', '川菜', 4.0, '深圳');

INSERT INTO dishes VALUES (101, 1, '麻婆豆腐',  28, 1);
INSERT INTO dishes VALUES (102, 1, '宫保鸡丁',  38, 1);
INSERT INTO dishes VALUES (103, 1, '米饭',       3, 0);
INSERT INTO dishes VALUES (104, 2, '白切鸡',    68, 1);
INSERT INTO dishes VALUES (105, 2, '虾饺',      36, 1);
INSERT INTO dishes VALUES (106, 2, '叉烧',      48, 0);
INSERT INTO dishes VALUES (107, 3, '三文鱼刺身',88, 1);
INSERT INTO dishes VALUES (108, 3, '加州卷',    36, 0);
INSERT INTO dishes VALUES (109, 4, '意大利肉酱面',58, 1);
INSERT INTO dishes VALUES (110, 4, '凯撒沙拉',  42, 0);
INSERT INTO dishes VALUES (111, 5, '香辣麻辣烫',32, 1);
INSERT INTO dishes VALUES (112, 5, '酸梅汤',    8,  0);

INSERT INTO customers VALUES (1, '小林', '北京');
INSERT INTO customers VALUES (2, '小江', '北京');
INSERT INTO customers VALUES (3, '小郑', '上海');
INSERT INTO customers VALUES (4, '小冯', '上海');
INSERT INTO customers VALUES (5, '小陈', '深圳');

INSERT INTO orders VALUES (1, 1, 1, '2024-11-01 12:30', 'delivered', 4);
INSERT INTO orders VALUES (2, 1, 2, '2024-11-05 19:00', 'delivered', 6);
INSERT INTO orders VALUES (3, 2, 1, '2024-11-08 18:30', 'delivered', 4);
INSERT INTO orders VALUES (4, 2, 2, '2024-11-15 12:00', 'cancelled', 0);
INSERT INTO orders VALUES (5, 3, 3, '2024-11-02 19:30', 'delivered', 8);
INSERT INTO orders VALUES (6, 3, 4, '2024-11-12 13:00', 'delivered', 5);
INSERT INTO orders VALUES (7, 4, 4, '2024-11-09 20:00', 'delivered', 5);
INSERT INTO orders VALUES (8, 5, 5, '2024-11-04 12:00', 'delivered', 3);
INSERT INTO orders VALUES (9, 5, 5, '2024-11-18 21:30', 'delivered', 3);
INSERT INTO orders VALUES (10,1, 1, '2024-11-25 19:30', 'pending',   4);

INSERT INTO order_items VALUES (1, 1, 101, 1, 28);
INSERT INTO order_items VALUES (2, 1, 102, 1, 38);
INSERT INTO order_items VALUES (3, 1, 103, 2, 3);
INSERT INTO order_items VALUES (4, 2, 104, 1, 68);
INSERT INTO order_items VALUES (5, 2, 105, 2, 36);
INSERT INTO order_items VALUES (6, 3, 102, 1, 38);
INSERT INTO order_items VALUES (7, 4, 105, 1, 36);
INSERT INTO order_items VALUES (8, 5, 107, 2, 88);
INSERT INTO order_items VALUES (9, 5, 108, 1, 36);
INSERT INTO order_items VALUES (10,6, 109, 1, 58);
INSERT INTO order_items VALUES (11,6, 110, 1, 42);
INSERT INTO order_items VALUES (12,7, 109, 2, 58);
INSERT INTO order_items VALUES (13,8, 111, 1, 32);
INSERT INTO order_items VALUES (14,8, 112, 2, 8);
INSERT INTO order_items VALUES (15,9, 111, 2, 32);
INSERT INTO order_items VALUES (16,10,101, 1, 28);
INSERT INTO order_items VALUES (17,10,102, 1, 38);
""".strip(),

    "博客社交系统": """
-- 博客社交系统：用户、文章、评论、点赞、关注
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    register_date TEXT,
    follower_count INTEGER DEFAULT 0
);

CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    author_id INTEGER,
    title TEXT NOT NULL,
    category TEXT,
    publish_date TEXT,
    view_count INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES users(user_id)
);

CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY,
    post_id INTEGER,
    user_id INTEGER,
    content TEXT,
    comment_time TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE likes (
    like_id INTEGER PRIMARY KEY,
    post_id INTEGER,
    user_id INTEGER,
    like_time TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE follows (
    follower_id INTEGER,
    followed_id INTEGER,
    follow_date TEXT,
    PRIMARY KEY (follower_id, followed_id),
    FOREIGN KEY (follower_id) REFERENCES users(user_id),
    FOREIGN KEY (followed_id) REFERENCES users(user_id)
);

INSERT INTO users VALUES (1, 'alice',  '2022-03-10', 1200);
INSERT INTO users VALUES (2, 'bob',    '2022-06-20', 380);
INSERT INTO users VALUES (3, 'carol',  '2023-01-05', 5800);
INSERT INTO users VALUES (4, 'david',  '2023-04-15', 90);
INSERT INTO users VALUES (5, 'eve',    '2023-09-01', 0);
INSERT INTO users VALUES (6, 'frank',  '2024-02-20', 25);
INSERT INTO users VALUES (7, 'grace',  '2024-07-10', NULL);

INSERT INTO posts VALUES (1, 1, 'SQL 入门十讲',     '技术', '2024-09-01', 5800);
INSERT INTO posts VALUES (2, 1, 'JOIN 比较全攻略',  '技术', '2024-10-12', 3200);
INSERT INTO posts VALUES (3, 2, '我的咖啡日常',     '生活', '2024-09-20', 580);
INSERT INTO posts VALUES (4, 3, '深度学习简史',     '技术', '2024-08-15', 12000);
INSERT INTO posts VALUES (5, 3, 'GPT 时代的写作',   '观点', '2024-10-05', 8500);
INSERT INTO posts VALUES (6, 3, '城市旅行 vs 山野', '生活', '2024-11-01', 2100);
INSERT INTO posts VALUES (7, 4, '我的第一篇',       '随笔', '2024-10-20', 80);
INSERT INTO posts VALUES (8, 6, '运动周记 #1',      '生活', '2024-11-05', 35);

INSERT INTO comments VALUES (1, 1, 2, '写得真清楚！',   '2024-09-02 10:00');
INSERT INTO comments VALUES (2, 1, 3, '收藏了',         '2024-09-03 14:30');
INSERT INTO comments VALUES (3, 1, 4, '请问有视频吗？', '2024-09-05 09:00');
INSERT INTO comments VALUES (4, 2, 4, '正好需要',       '2024-10-13 11:30');
INSERT INTO comments VALUES (5, 4, 1, '强！',           '2024-08-16 21:00');
INSERT INTO comments VALUES (6, 4, 2, '收藏 +1',        '2024-08-18 08:00');
INSERT INTO comments VALUES (7, 4, 5, '什么时候出 part 2', '2024-09-01 12:00');
INSERT INTO comments VALUES (8, 5, 6, '同感',           '2024-10-06 19:00');
INSERT INTO comments VALUES (9, 6, 1, '想去山野',       '2024-11-02 10:30');

INSERT INTO likes VALUES (1, 1, 2, '2024-09-01 12:00');
INSERT INTO likes VALUES (2, 1, 3, '2024-09-02 09:00');
INSERT INTO likes VALUES (3, 1, 4, '2024-09-03 22:00');
INSERT INTO likes VALUES (4, 2, 3, '2024-10-12 18:00');
INSERT INTO likes VALUES (5, 4, 1, '2024-08-15 21:00');
INSERT INTO likes VALUES (6, 4, 2, '2024-08-16 09:00');
INSERT INTO likes VALUES (7, 4, 5, '2024-08-30 12:00');
INSERT INTO likes VALUES (8, 4, 6, '2024-09-05 16:00');
INSERT INTO likes VALUES (9, 5, 1, '2024-10-05 11:00');
INSERT INTO likes VALUES (10,5, 6, '2024-10-08 20:00');
INSERT INTO likes VALUES (11,6, 5, '2024-11-01 14:00');
INSERT INTO likes VALUES (12,3, 1, '2024-09-21 10:00');

INSERT INTO follows VALUES (2, 1, '2022-07-01');
INSERT INTO follows VALUES (4, 1, '2023-05-20');
INSERT INTO follows VALUES (5, 1, '2023-10-10');
INSERT INTO follows VALUES (1, 3, '2023-02-01');
INSERT INTO follows VALUES (2, 3, '2023-03-15');
INSERT INTO follows VALUES (4, 3, '2023-08-01');
INSERT INTO follows VALUES (5, 3, '2023-09-10');
INSERT INTO follows VALUES (6, 3, '2024-03-01');
INSERT INTO follows VALUES (1, 2, '2022-08-10');
INSERT INTO follows VALUES (3, 2, '2022-12-05');
""".strip(),
}


def get_preset(domain: str) -> str:
    """获取预置 schema SQL；若没有则返回空串。"""
    return PRESET_SCHEMAS.get(domain, "")


def list_presets() -> list:
    return list(PRESET_SCHEMAS.keys())
