-- Ensure app user uses mysql_native_password
ALTER USER 'appuser'@'%' IDENTIFIED WITH mysql_native_password BY 'apppassword';

GRANT ALL PRIVILEGES ON supermarketdb.* TO 'appuser'@'%';

FLUSH PRIVILEGES;
