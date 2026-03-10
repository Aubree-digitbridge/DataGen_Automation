insert into ProductBasicAttributeRelationship
(
    MasterAccountNum,
    ProfileNum,
    DatabaseNum,
    BasicAttributeNum,
    CentralProductNum,
    BasicAttributeValue,
    CreateBy,
    UpdateBy,
    CreateDate,
    UpdateDate
)
select 
    10057 as MasterAccountNum,
    10127 as ProfileNum,
    1084  as DatabaseNum,
    1031  as BasicAttributeNum,
    t2.CentralProductNum,
    t1.BasicAttributeValue,
    null as CreateBy,
    null as UpdateBy,
    getdate() as CreateDate,
    getdate() as UpdateDate
from 
(
    select p.SKU, p.CentralProductNum, p.SubStyleCode, p.ProductType, a.BasicAttributeValue
    from productBasic p
    left join ProductBasicAttributeRelationship a
        on p.CentralProductNum = a.CentralProductNum
       and a.BasicAttributeNum = 1031
       and a.MasterAccountNum = 10057
       and a.ProfileNum = 10127
    where p.MasterAccountNum = 10057
      and p.ProfileNum = 10127
      and p.ProductType = 3
) t1
inner join
(
    select p.SKU, p.CentralProductNum, p.SubStyleCode, p.ProductType, a.BasicAttributeValue
    from productBasic p
    left join ProductBasicAttributeRelationship a
        on p.CentralProductNum = a.CentralProductNum
       and a.BasicAttributeNum = 1031
       and a.MasterAccountNum = 10057
       and a.ProfileNum = 10127
    where p.MasterAccountNum = 10057
      and p.ProfileNum = 10127
      and p.ProductType = 1
) t2
    on t1.SubStyleCode = t2.SubStyleCode
where t1.BasicAttributeValue is not null
  and t2.BasicAttributeValue is null