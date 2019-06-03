create table users
(
    id       serial not null
        constraint users_pk
            primary key,
    username text   not null,
    pw_hash  text   not null
);

alter table users
    owner to bence;

create unique index users_pw_hash_uindex
    on users (pw_hash);

create unique index users_user_id_uindex
    on users (id);

create unique index users_username_uindex
    on users (username);

