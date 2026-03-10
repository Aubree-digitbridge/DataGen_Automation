
declare @shipDate datetime
set @shipDate = DATEADD(DAY, 2, GETDATE())

select i.ChannelOrderID as 'Channel Order ID',o.ShipDate as 'Ship Date','UTC-8' as 'TimeZone', 'FedEx' as 'Carrier','' as 'Tracking Number',
'' AS [Shipping Service],
    '' AS [2nd Tracking Number],
    '' AS [Package],
    '' AS [Shipping Fee],
    '' AS [Weight],
    '' AS [Length],
    '' AS [Width],
    '' AS [Height],
    '' AS [Note],
pi.SKU, pi.OrderQty as 'Ship Qty', i.ChannelAccountNum
--, i.ChannelNum, o.OrderNumber  

from 
(select SalesOrderUuid, OrderDate, ShipDate, OrderNumber from SalesOrderHeader (nolock) pb
WHERE pb.MasterAccountNum =10057 AND pb.ProfileNum =10127 and OrderStatus not in(4,255) and OrderNumber like '2000%' and ShipDate <@shipDate )o
left join SalesOrderHeaderInfo (nolock) i
on o.SalesOrderUuid = i.SalesOrderUuid
left join SalesOrderItems (nolock) pi
on o.SalesOrderUuid = pi.SalesOrderUuid
order by ChannelAccountNum, [Channel Order ID]
