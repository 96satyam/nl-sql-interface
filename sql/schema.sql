-- Drop tables in reverse order of dependency to avoid foreign key errors
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS products;

-- Create the departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Create the employees table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER,
    email VARCHAR(255) UNIQUE NOT NULL,
    salary DECIMAL(10, 2),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- Create the orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    employee_id INTEGER,
    order_total DECIMAL(10, 2),
    order_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Create the products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2)
);

-- Create indexes on frequently searched columns for performance
CREATE INDEX idx_employee_name ON employees(name);
CREATE INDEX idx_product_name ON products(name);
CREATE INDEX idx_customer_name ON orders(customer_name);