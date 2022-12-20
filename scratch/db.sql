-- setup validation attributes in contributors table
alter table contributors drop column collaborators;
alter table contributors drop column collections;

alter table contributors add column collaborators integer[] not null default '{}';
alter table contributors add column collections integer[] not null default '{}';

update contributors set collaborators = '{1,2,3,4,5}' where id = 1;
update contributors set collaborators = '{2}', collections = '{11}'  where id = 2;
update contributors set collaborators = '{3}' where id = 3;
update contributors set collaborators = '{4}' where id = 4;
update contributors set collaborators = '{5}' where id = 5;

-- validate user access to data
select * from facebook where country = 'UA' and
(
collection_id in (select unnest(collections) from contributors where id=1) or
contributor_id in (select unnest(collaborators) from contributors where id=1)
);

select * from facebook where collection_id in (
	select unnest(collections) from contributors where id=2
);

select * from facebook where contributor_id in (
	select unnest(collaborators) from contributors where id=1
);


select * from facebook where collection_id = (
	select id from collections where name = 'dgg_national'
);

select distinct country from facebook where contributor_id = 5 order by country asc;

-- add partitions for additional countries
create table facebook_NU partition of facebook for values in ('NU');
create table facebook_SJ partition of facebook for values in ('SJ');
create table facebook_TK partition of facebook for values in ('TK');
create table facebook_PN partition of facebook for values in ('PN');
create table facebook_CX partition of facebook for values in ('CX');
create table facebook_AN partition of facebook for values in ('AN');
create table facebook_GS partition of facebook for values in ('GS');
create table facebook_AQ partition of facebook for values in ('AQ');
create table facebook_UM partition of facebook for values in ('UM');
create table facebook_IO partition of facebook for values in ('IO');
create table facebook_VA partition of facebook for values in ('VA');

create table instagram_NU partition of instagram for values in ('NU');
create table instagram_SJ partition of instagram for values in ('SJ');
create table instagram_TK partition of instagram for values in ('TK');
create table instagram_PN partition of instagram for values in ('PN');

create table instagram_CX partition of instagram for values in ('CX');
create table instagram_AN partition of instagram for values in ('AN');
create table instagram_GS partition of instagram for values in ('GS');
create table instagram_AQ partition of instagram for values in ('AQ');
create table instagram_UM partition of instagram for values in ('UM');
create table instagram_IO partition of instagram for values in ('IO');
create table instagram_VA partition of instagram for values in ('VA');

