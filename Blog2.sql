DROP TABLE Comments CASCADE CONSTRAINTS PURGE;
DROP TABLE Article_tag CASCADE CONSTRAINTS PURGE;
DROP TABLE Tags CASCADE CONSTRAINTS PURGE;
DROP TABLE Article_Categorie CASCADE CONSTRAINTS PURGE;
DROP TABLE Categories CASCADE CONSTRAINTS PURGE;
DROP TABLE Articles CASCADE CONSTRAINTS PURGE;
DROP TABLE T_Users CASCADE CONSTRAINTS PURGE;

CREATE TABLE T_Users
(
    email      VARCHAR2(30) NULL,
    name_user  VARCHAR2(30) NOT NULL,
    pass   VARCHAR2(100) NOT NULL
);
CREATE UNIQUE INDEX XPKT_Users ON T_Users(name_user ASC);
CREATE UNIQUE INDEX UK_T_Users_Email ON T_Users(email ASC);
ALTER TABLE T_Users
    ADD CONSTRAINT XPKT_Users PRIMARY KEY (name_user);

CREATE TABLE Categories
(
    cat_name VARCHAR2(30) NOT NULL,
    c_url    VARCHAR2(30) NULL
);
CREATE UNIQUE INDEX XPKCategories ON Categories(cat_name ASC);
ALTER TABLE Categories
    ADD CONSTRAINT XPKCategories PRIMARY KEY (cat_name);

CREATE TABLE Tags
(
    tag_name VARCHAR2(30) NOT NULL,
    t_url    VARCHAR2(200) NULL
);
CREATE UNIQUE INDEX XPKTags ON Tags(tag_name ASC);
ALTER TABLE Tags
    ADD CONSTRAINT XPKTags PRIMARY KEY (tag_name);

CREATE TABLE Articles
(
    title      VARCHAR2(50) NULL,
    article_id INTEGER NOT NULL,
    name_user  VARCHAR2(30) NOT NULL,
    a_text     VARCHAR2(2000) NULL,
    a_date     DATE NULL
);
CREATE UNIQUE INDEX XPKArticles ON Articles(article_id ASC);
ALTER TABLE Articles
    ADD CONSTRAINT XPKArticles PRIMARY KEY (article_id);
ALTER TABLE Articles
    ADD CONSTRAINT R_2 FOREIGN KEY (name_user) REFERENCES T_Users(name_user);

CREATE TABLE Comments
(
    id_comment NUMBER NOT NULL,
    article_id INTEGER NOT NULL,
    name_user  VARCHAR2(30) NOT NULL,
    c_date     DATE NULL,
    c_text     VARCHAR2(500) NULL
);
CREATE UNIQUE INDEX XPKComments ON Comments(id_comment ASC);
ALTER TABLE Comments
    ADD CONSTRAINT XPKComments PRIMARY KEY (id_comment);
ALTER TABLE Comments
    ADD CONSTRAINT R_3 FOREIGN KEY (article_id) REFERENCES Articles(article_id);
ALTER TABLE Comments
    ADD CONSTRAINT R_1 FOREIGN KEY (name_user) REFERENCES T_Users(name_user);

CREATE TABLE Article_Categorie
(
    article_id INTEGER NOT NULL,
    cat_name   VARCHAR2(30) NOT NULL
);
CREATE UNIQUE INDEX XPKArticle_Categorie ON Article_Categorie(article_id ASC, cat_name ASC);
ALTER TABLE Article_Categorie
    ADD CONSTRAINT XPKArticle_Categorie PRIMARY KEY (article_id, cat_name);
ALTER TABLE Article_Categorie
    ADD CONSTRAINT R_7 FOREIGN KEY (article_id) REFERENCES Articles(article_id);
ALTER TABLE Article_Categorie
    ADD CONSTRAINT R_8 FOREIGN KEY (cat_name) REFERENCES Categories(cat_name);

CREATE TABLE Article_tag
(
    article_id INTEGER NOT NULL,
    tag_name   VARCHAR2(30) NOT NULL
);
CREATE UNIQUE INDEX XPKArticle_tag ON Article_tag(article_id ASC, tag_name ASC);
ALTER TABLE Article_tag
    ADD CONSTRAINT XPKArticle_tag PRIMARY KEY (article_id, tag_name);
ALTER TABLE Article_tag
    ADD CONSTRAINT R_6 FOREIGN KEY (article_id) REFERENCES Articles(article_id);
ALTER TABLE Article_tag
    ADD CONSTRAINT R_5 FOREIGN KEY (tag_name) REFERENCES Tags(tag_name);
    
INSERT INTO Categories (cat_name, c_url) VALUES ('Terror', 'terror');
INSERT INTO Categories (cat_name, c_url) VALUES ('Comedia', 'comedia');
INSERT INTO Categories (cat_name, c_url) VALUES ('Romance', 'romance');
INSERT INTO Categories (cat_name, c_url) VALUES ('Suspenso', 'suspenso');
INSERT INTO Categories (cat_name, c_url) VALUES ('Accion', 'accion');
INSERT INTO Categories (cat_name, c_url) VALUES ('Ficcion', 'ficcion');
INSERT INTO Categories (cat_name, c_url) VALUES ('Musical', 'musical');

commit;
    
--Categorias 
CREATE OR REPLACE FUNCTION get_all_categories
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT cat_name
        FROM Categories
        ORDER BY cat_name;

    RETURN v_cursor;
END;

--Tags of an article
CREATE OR REPLACE FUNCTION get_tags_by_article(p_article_id IN INTEGER)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT tag_name
        FROM Article_tag
        WHERE article_id = p_article_id
        ORDER BY tag_name;

    RETURN v_cursor;
END;

--users 
--Verificar
CREATE OR REPLACE FUNCTION get_user_name(p_email IN VARCHAR2, p_pass IN VARCHAR2)
RETURN VARCHAR2
IS
    v_name_user VARCHAR2(30);
BEGIN
    SELECT NAME_USER
    INTO v_name_user
    FROM T_USERS
    WHERE EMAIL = p_email AND PASS = p_pass;

    RETURN v_name_user;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
    WHEN OTHERS THEN
        RETURN NULL;
END;

create or replace FUNCTION get_user_name2(p_email IN VARCHAR2)
RETURN VARCHAR2
IS
    v_name_user VARCHAR2(30);
BEGIN
    SELECT NAME_USER
    INTO v_name_user
    FROM T_USERS
    WHERE EMAIL = p_email;

    RETURN v_name_user;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
    WHEN OTHERS THEN
        RETURN NULL;
END;

--agregar
CREATE OR REPLACE PROCEDURE add_user (
    p_name_user IN VARCHAR2,
    p_email     IN VARCHAR2,
    p_pass in VARCHAR
) AS
BEGIN
    INSERT INTO T_Users (name_user, email, pass )
    VALUES (p_name_user, p_email, p_pass);
EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
        RAISE_APPLICATION_ERROR(-20101, 'El usuario ya existe.');
END;

--update password
CREATE OR REPLACE PROCEDURE update_user_password (
    p_name_user IN VARCHAR2,
    p_pass  IN VARCHAR2
) AS
BEGIN
    UPDATE T_Users
    SET pass = p_pass
    WHERE name_user = p_name_user;

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20104, 'Usuario no encontrado.');
    END IF;
END;

--get email
CREATE OR REPLACE FUNCTION get_user_email(p_name_user IN VARCHAR2)
RETURN VARCHAR2
IS
    v_email VARCHAR2(30);
BEGIN
    SELECT email
    INTO v_email
    FROM T_Users
    WHERE name_user = p_name_user;

    RETURN v_email;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
    WHEN OTHERS THEN
        RETURN NULL;
END;

--delete
CREATE OR REPLACE PROCEDURE delete_user (
    p_name_user IN VARCHAR2
) AS
    v_user_exists NUMBER;
BEGIN

    SELECT COUNT(*) INTO v_user_exists 
    FROM T_Users 
    WHERE name_user = p_name_user;
    
    IF v_user_exists = 0 THEN
        RAISE_APPLICATION_ERROR(-20103, 'Usuario no encontrado.');
    END IF;

    DELETE FROM Comments 
    WHERE article_id IN (
        SELECT article_id FROM Articles WHERE name_user = p_name_user
    );

    DELETE FROM Comments 
    WHERE name_user = p_name_user;

    DELETE FROM Article_tag 
    WHERE article_id IN (
        SELECT article_id FROM Articles WHERE name_user = p_name_user
    );

    DELETE FROM Article_Categorie 
    WHERE article_id IN (
        SELECT article_id FROM Articles WHERE name_user = p_name_user
    );

    DELETE FROM Articles 
    WHERE name_user = p_name_user;

    DELETE FROM T_Users 
    WHERE name_user = p_name_user;

    COMMIT;
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END;


--article
CREATE OR REPLACE FUNCTION get_article_by_id(p_article_id IN INTEGER)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT article_id, title, name_user, a_text
        FROM Articles
        WHERE article_id = p_article_id;

    RETURN v_cursor;
END;


-- articles by category
CREATE OR REPLACE FUNCTION get_articles_by_category(p_cat_name IN VARCHAR2)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT a.article_id, a.title, a.name_user, a.a_text
        FROM Articles a
        JOIN Article_Categorie ac ON a.article_id = ac.article_id
        WHERE ac.cat_name = p_cat_name;

    RETURN v_cursor;
END;

--articles by tag
CREATE OR REPLACE FUNCTION get_articles_by_tag(p_tag_name IN VARCHAR2)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT a.article_id, a.title, a.name_user, a.a_text
        FROM Articles a
        JOIN Article_tag at ON a.article_id = at.article_id
        WHERE at.tag_name = p_tag_name;

    RETURN v_cursor;
END;

--Articles of an author
CREATE OR REPLACE FUNCTION get_articles_by_author(p_name_user IN VARCHAR2)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT article_id, title, a_date, a_text
        FROM Articles
        WHERE name_user = p_name_user
        ORDER BY a_date DESC;

    RETURN v_cursor;
END;

--comments of an article
CREATE OR REPLACE FUNCTION get_comments_by_article(p_article_id IN INTEGER)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT name_user, c_date, c_text
        FROM Comments
        WHERE article_id = p_article_id
        ORDER BY c_date;
        
    RETURN v_cursor;
END;


--Secuencia para article_id
CREATE SEQUENCE article_seq
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;


--Article 
--agregar
CREATE OR REPLACE FUNCTION add_article(
    p_title     IN VARCHAR2,
    p_name_user IN VARCHAR2,
    p_a_text    IN VARCHAR2
) RETURN NUMBER
IS
    v_article_id NUMBER;
BEGIN
    v_article_id := article_seq.NEXTVAL;

    INSERT INTO Articles (article_id, title, name_user, a_text, a_date)
    VALUES (v_article_id, p_title, p_name_user, p_a_text, SYSDATE);

    RETURN v_article_id;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;

--Agregar un article-tag
CREATE OR REPLACE FUNCTION add_article_tag(
    p_article_id IN INTEGER,
    p_tag_name   IN VARCHAR2
) RETURN VARCHAR2
IS
BEGIN
    INSERT INTO Article_tag (article_id, tag_name)
    VALUES (p_article_id, p_tag_name);

    RETURN 'Relación tag agregada';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error al agregar tag: ' || SQLERRM;
END;

--Agregar article category
create or replace FUNCTION add_article_category(
    p_article_id IN INTEGER,
    p_cat_name   IN VARCHAR2
) RETURN VARCHAR2
IS
BEGIN
    INSERT INTO Article_Categorie (article_id, cat_name)
    VALUES (p_article_id, p_cat_name);

    RETURN 'Relación categoría agregada';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error al agregar categoría: ' || SQLERRM;
END;

--eliminar
CREATE OR REPLACE PROCEDURE delete_article (
    p_article_id IN NUMBER
) AS
BEGIN
    DELETE FROM Comments
    WHERE article_id = p_article_id;

    DELETE FROM Article_Categorie
    WHERE article_id = p_article_id;

    DELETE FROM Article_tag
    WHERE article_id = p_article_id;

    DELETE FROM Articles
    WHERE article_id = p_article_id;

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20203, 'Artículo no encontrado.');
    END IF;
END;

--Comentarios articulo
CREATE SEQUENCE comment_seq
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

--agregar
CREATE OR REPLACE FUNCTION add_comment(
    p_article_id IN INTEGER,
    p_name_user  IN VARCHAR2,
    p_c_text     IN VARCHAR2
) RETURN VARCHAR2
IS
    v_id_comment NUMBER;
BEGIN
    v_id_comment := comment_seq.NEXTVAL;

    INSERT INTO Comments (id_comment, article_id, name_user, c_date, c_text)
    VALUES (v_id_comment, p_article_id, p_name_user, SYSDATE, p_c_text);

    RETURN 'Comentario agregado con ID: ' || v_id_comment;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error al agregar comentario: ' || SQLERRM;
END;


--Tags
--agregar
CREATE OR REPLACE FUNCTION insert_tag_if_not_exists(p_tag_name IN VARCHAR2)
RETURN VARCHAR2
IS
    v_exists NUMBER := 0;
    v_url    VARCHAR2(4000);
BEGIN
    SELECT COUNT(*) INTO v_exists
    FROM tags
    WHERE LOWER(tag_name) = LOWER(p_tag_name);

    IF v_exists = 0 THEN
        v_url := 'https://example.com/tags/' || LOWER(p_tag_name);

        INSERT INTO tags (tag_name, t_url)
        VALUES (p_tag_name, v_url);

        RETURN 'Tag insertado: ' || p_tag_name;
    ELSE
        RETURN 'Tag ya existe: ' || p_tag_name;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
END;

create or replace FUNCTION get_cat_by_article(p_article_id IN INTEGER)
RETURN SYS_REFCURSOR
IS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT cat_name
        FROM article_categorie
        WHERE article_id = p_article_id
        ORDER BY cat_name;

    RETURN v_cursor;
END;