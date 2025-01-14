import uiautomator2 as u2


host_id = 101
port_id = 42653

d = u2.connect(f'192.168.2.{host_id}:{port_id}') 

if not d.info["naturalOrientation"]:
    exit("手机连接失败！！！！")



# d(resourceId="android:id/summary").click()
# get the children or grandchildren
print(d.dump_hierarchy())


