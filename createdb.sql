create table review(
    id integer primary key,
    from_id integer NOT NULL,
    user_id integer NOT NULL,
    message varchar(255),
    FOREIGN KEY(user_id) REFERENCES user(id)
);

create table rating(
    from_id integer NOT NULL,
    user_id integer NOT NULL,
    likes integer,
    dislikes integer,
    FOREIGN KEY(user_id) REFERENCES user(id),
    UNIQUE(from_id)
);

create table user(
    id integer NOT NULL,
    name varchar(255) NOT NULL,
    last_name varchar(255) NOT NULL,
    phone_number varchar(255),
    photo blob,
    UNIQUE(id)
);
