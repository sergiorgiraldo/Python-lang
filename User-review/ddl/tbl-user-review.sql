create table tbl_user_review (
    user_corp_key varchar(10),
    review_cycle varchar(6),
    auth_key varchar(100),
    date_sent date,
    date_received date null,
    status char(1),
    PRIMARY KEY(user_corp_key, review_cycle)
)