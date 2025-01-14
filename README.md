
```cmd

.\.venv\Scripts\activate

uiauto.dev

```



# 命令行
其中的`$device_ip`代表设备的IP地址

如需指定设备，需要传入`--serial`，如 `python3 -m uiautomator2 --serial bff1234 <SubCommand>`，`SubCommand`为子命令（screenshot, current 等）

> 1.0.3 添加：`python3 -m uiautomator2` 等同于 `uiautomator2`

- screenshot: 截图

    ```bash
    $ uiautomator2 screenshot screenshot.jpg
    ```

- current: 获取当前包名和活动

    ```bash
    $ uiautomator2 current
    {
        "package": "com.android.browser",
        "activity": "com.uc.browser.InnerUCMobile",
        "pid": 28478
    }
    ```
    
- uninstall：卸载应用

    ```bash
    $ uiautomator2 uninstall <package-name> # 卸载一个包
    $ uiautomator2 uninstall <package-name-1> <package-name-2> # 卸载多个包
    $ uiautomator2 uninstall --all # 卸载所有包
    ```

- stop: 停止应用

    ```bash
    $ uiautomator2 stop com.example.app # 停止一个app
    $ uiautomator2 stop --all # 停止所有app
    ```

- doctor:

    ```bash
    $ uiautomator2 doctor
    [I 2024-04-25 19:53:36,288 __main__:101 pid:15596] uiautomator2 一切正常
    ```
    
# API 文档

### 新命令超时（已移除）
当 Python 退出时，UiAutomation 服务也会退出。
<!-- 客户端发出新命令前，等待的最大时间（单位秒），默认 3 分钟。如果超时，则假定客户端退出并结束 uiautomator 服务。

配置辅助服务的最大空闲时间，超时将自动释放。默认 3 分钟。

```python
d.set_new_command_timeout(300) # 设置为 5 分钟，单位为秒
``` -->

### 调试 HTTP 请求
打印出代码背后的 HTTP 请求信息

```python
>>> d.debug = True
>>> d.info
12:32:47.182 $ curl -X POST -d '{"jsonrpc": "2.0", "id": "b80d3a488580be1f3e9cb3e926175310", "method": "deviceInfo", "params": {}}' 'http://127.0.0.1:54179/jsonrpc/0'
12:32:47.225 响应 >>>
{"jsonrpc":"2.0","id":"b80d3a488580be1f3e9cb3e926175310","result":{"currentPackageName":"com.android.mms","displayHeight":1920,"displayRotation":0,"displaySizeDpX":360,"displaySizeDpY":640,"displayWidth":1080,"productName":"odin","screenOn":true,"sdkInt":25,"naturalOrientation":true}}
<<< 结束
```

### 隐式等待
设置元素查找等待时间（默认 20 秒）

```python
d.implicitly_wait(10.0) # 也可以通过 d.settings['wait_timeout'] = 10.0 修改
d(text="Settings").click() # 如果设置按钮 10 秒内未显示，将引发 UiObjectNotFoundError

print("等待超时", d.implicitly_wait()) # 获取默认的隐式等待时间
```

此功能会影响 `click`、`long_click`、`drag_to`、`get_text`、`set_text`、`clear_text` 等操作。

## 应用管理
这一部分展示了如何进行应用管理

### 安装应用
我们只支持从 URL 安装 APK

```python
d.app_install('http://some-domain.com/some.apk')
```

### 启动应用
```python
# 默认方法是先通过 atx-agent 解析 apk 包的 mainActivity，然后调用 am start -n $package/$activity 启动
d.app_start("com.example.hello_world")

# 使用 monkey -p com.example.hello_world -c android.intent.category.LAUNCHER 1 启动
# 这种方法有一个副作用，它会自动关闭手机的旋转锁定
d.app_start("com.example.hello_world", use_monkey=True) # 通过包名启动

# 通过指定 main activity 启动应用，等同于调用 am start -n com.example.hello_world/.MainActivity
d.app_start("com.example.hello_world", ".MainActivity")
```

### 停止应用
```python
# 等效于 `am force-stop`，因此可能会丢失数据
d.app_stop("com.example.hello_world") 
# 等效于 `pm clear`
d.app_clear('com.example.hello_world')
```

### 停止所有运行中的应用
```python
# 停止所有应用
d.app_stop_all()
# 停止所有应用，排除 com.examples.demo
d.app_stop_all(excludes=['com.examples.demo'])
```

### 获取应用信息
```python
d.app_info("com.examples.demo")
# 预期输出
#{
#    "mainActivity": "com.github.uiautomator.MainActivity",
#    "label": "ATX",
#    "versionName": "1.1.7",
#    "versionCode": 1001007,
#    "size":1760809
#}

# 保存应用图标
img = d.app_icon("com.examples.demo")
img.save("icon.png")
```

### 列出所有正在运行的应用
```python
d.app_list_running()
# 预期输出
# ["com.xxxx.xxxx", "com.github.uiautomator", "xxxx"]
```

### 等待应用运行
```python
pid = d.app_wait("com.example.android") # 等待应用运行，返回 pid（整数）
if not pid:
    print("com.example.android 未运行")
else:
    print("com.example.android 的 pid 是 %d" % pid)

d.app_wait("com.example.android", front=True) # 等待应用在前台运行
d.app_wait("com.example.android", timeout=20.0) # 最长等待时间为 20 秒（默认）
```

> 版本 1.2.0 中新增

### 文件推送与拉取
* 推送文件到设备

    ```python
    # 推送到一个文件夹
    d.push("foo.txt", "/sdcard/")
    # 推送并重命名
    d.push("foo.txt", "/sdcard/bar.txt")
    # 推送文件对象
    with open("foo.txt", 'rb') as f:
        d.push(f, "/sdcard/")
    # 推送并更改文件访问模式
    d.push("foo.sh", "/data/local/tmp/", mode=0o755)
    ```

* 从设备拉取文件

    ```python
    d.pull("/sdcard/tmp.txt", "tmp.txt")

    # 如果文件在设备上找不到，将引发 FileNotFoundError
    d.pull("/sdcard/some-file-not-exists.txt", "tmp.txt")
    ```

### 其他应用操作

```python
# 授予所有权限
d.app_auto_grant_permissions("io.appium.android.apis")

# 打开 scheme
d.open_url("appname://appnamehost")
# 等同于
# adb shell am start -a android.intent.action.VIEW -d "appname://appnamehost"
```

## 基本 API 用法
这一部分展示了如何执行常见的设备操作：

### Shell 命令
* 运行短时间内的 shell 命令，并设置超时保护（默认超时 60 秒）

    注意：超时支持需要 `atx-agent >=0.3.3`

    `adb_shell` 函数已弃用，请使用 `shell` 函数。

    简单用法

    ```python
    output, exit_code = d.shell("pwd", timeout=60) # 超时 60 秒（默认）
    # output: "/\n", exit_code: 0
    # 类似于命令：adb shell pwd

    # 由于 `shell` 函数的返回类型是 `namedtuple("ShellResponse", ("output", "exit_code"))`
    # 所以可以做一些技巧
    output = d.shell("pwd").output
    exit_code = d.shell("pwd").exit_code
    ```

    第一个参数也可以是列表，例如：

    ```python
    output, exit_code = d.shell(["ls", "-l"])
    # output: "/....", exit_code: 0
    ```

    这将返回标准输出和标准错误合并后的字符串。
    如果命令是一个阻塞命令，`shell` 也会阻塞直到命令完成或超时。命令执行过程中不会接收部分输出。此 API 不适用于长时间运行的命令。给定的 shell 命令在类似于 `adb shell` 的环境中运行，具有 `adb` 或 `shell`（比应用权限更高）的 Linux 权限级别。

* 运行长时间运行的 shell 命令（已移除）
<!-- 
    添加 stream=True 将返回 `requests.models.Response` 对象。更多信息请参阅 [requests 流式处理](http://docs.python-requests.org/zh_CN/latest/user/quickstart.html#id5)

    ```python
    r = d.shell("logcat", stream=True)
    # r: requests.models.Response
    deadline = time.time() + 10 # 最长运行 10 秒
    try:
        for line in r.iter_lines(): # r.iter_lines(chunk_size=512, decode_unicode=None, delimiter=None)
            if time.time() > deadline:
                break
            print("读取:", line.decode('utf-8'))
    finally:
        r.close() # 必须调用此方法
    ```

    当调用 `r.close()` 时命令将被终止。-->
    
### 会话
会话代表一个应用生命周期。可以用于启动应用，检测应用崩溃。

* 启动和关闭应用

    ```python
    sess = d.session("com.netease.cloudmusic") # 启动网易云音乐
    sess.close() # 停止网易云音乐
    sess.restart() # 冷启动网易云音乐
    ```

* 使用 Python `with` 启动和关闭应用

    ```python
    with d.session("com.netease.cloudmusic") as sess:
        sess(text="Play").click()
    ```

* 附加到正在运行的应用

    ```python
    # 如果应用未运行则启动，若已在运行则跳过启动
    sess = d.session("com.netease.cloudmusic", attach=True)
    ```

* 检测应用崩溃

    ```python
    # 当应用仍在运行时
    sess(text="Music").click() # 操作正常

    # 如果应用崩溃或退出
    sess(text="Music").click() # 引发 SessionBrokenError
    # 会话下的其他函数调用也会引发 SessionBrokenError
    ```

    ```python
    # 检查会话是否正常
    # 警告：函数名可能会在未来更改
    sess.running() # 返回 True 或 False
    ```


### 获取设备信息

获取基本信息

```python
d.info
```

下面是可能的输出：

```
{'currentPackageName': 'com.android.systemui',
 'displayHeight': 1560,
 'displayRotation': 0,
 'displaySizeDpX': 360,
 'displaySizeDpY': 780,
 'displayWidth': 720,
 'naturalOrientation': True,
 'productName': 'ELE-AL00',
 'screenOn': True,
 'sdkInt': 29}
```

获取窗口大小

```python
print(d.window_size())
# 设备竖屏输出示例: (1080, 1920)
# 设备横屏输出示例: (1920, 1080)
```

获取当前应用信息。对于一些 Android 设备，输出可能为空（请参见 *输出示例 3*）

```python
print(d.app_current())
# 输出示例 1: {'activity': '.Client', 'package': 'com.netease.example', 'pid': 23710}
# 输出示例 2: {'activity': '.Client', 'package': 'com.netease.example'}
# 输出示例 3: {'activity': None, 'package': None}
```

等待活动

```python
d.wait_activity(".ApiDemos", timeout=10) # 默认超时时间 10 秒
# 输出：True 或 False
```

获取设备序列号

```python
print(d.serial)
# 输出示例：74aAEDR428Z9
```

获取 WLAN IP

```python
print(d.wlan_ip)
# 输出示例：10.0.0.1 或 None
```

~~获取详细设备信息~~ `d.device_info`

设备信息

```python
print(d.device_info)
```

下面是可能的输出：

```
{'arch': 'arm64-v8a',
 'brand': 'google',
 'model': 'sdk_gphone64_arm64',
 'sdk': 34,
 'serial': 'EMULATOR34X1X19X0',
 'version': 14}
```


### 剪贴板
获取或设置剪贴板内容

* 设置剪贴板内容

    ```python
    d.clipboard = 'hello-world'
    # 或者
    d.set_clipboard('hello-world', 'label')
    ```

* 获取剪贴板内容

> 获取剪贴板内容需要先调用 `d.set_input_ime()` 设置 IME（输入法）。

    ```python
    # 获取剪贴板内容
    print(d.clipboard)
    ```

### 按键事件

* 打开/关闭屏幕

    ```python
    d.screen_on() # 打开屏幕
    d.screen_off() # 关闭屏幕
    ```

* 获取当前屏幕状态

    ```python
    d.info.get('screenOn') # 需要 Android >= 4.4
    ```

* 按下硬件/软键

    ```python
    d.press("home") # 按下 home 键
    d.press("back") # 按下 back 键
    d.press(0x07, 0x02) # 按下键码 0x07 ('0') 并加上 META ALT (0x02)
    ```

* 当前支持的按键名称：

    - home
    - back
    - left
    - right
    - up
    - down
    - center
    - menu
    - search
    - enter
    - delete (或 del)
    - recent (最近应用)
    - volume_up
    - volume_down
    - volume_mute
    - camera
    - power

您可以在 [Android KeyEvent](https://developer.android.com/reference/android/view/KeyEvent.html) 查找所有的按键代码定义。

* 解锁屏幕

    ```python
    d.unlock()
    # 等价于
    # 1. press("power")
    # 2. 从左下角滑到右上角
    ```

### 与设备的手势交互

* 点击屏幕

    ```python
    d.click(x, y)
    ```

* 双击

    ```python
    d.double_click(x, y)
    d.double_click(x, y, 0.1) # 默认两个点击之间的时间间隔是 0.1 秒
    ```

* 长按屏幕

    ```python
    d.long_click(x, y)
    d.long_click(x, y, 0.5) # 长按 0.5 秒（默认）
    ```

* 滑动

    ```python
    d.swipe(sx, sy, ex, ey)
    d.swipe(sx, sy, ex, ey, 0.5) # 滑动 0.5 秒（默认）
    ```

* 扩展滑动功能

    ```python
    d.swipe_ext("right") # 手指右滑，四选一 "left", "right", "up", "down"
    d.swipe_ext("right", scale=0.9) # 默认值为 0.9，滑动距离为屏幕宽度的 90%
    d.swipe_ext("right", box=(0, 0, 100, 100)) # 在 (0, 0) -> (100, 100) 区域做滑动

    # 实践中，上滑或下滑时，从中点开始滑动成功率较高
    d.swipe_ext("up", scale=0.8) # 代码会 vkk

    # 还可以使用 Direction 作为参数
    from uiautomator2 import Direction
    
    d.swipe_ext(Direction.FORWARD) # 页面下翻，等同于 d.swipe_ext("up")，只是更易理解
    d.swipe_ext(Direction.BACKWARD) # 页面上翻
    d.swipe_ext(Direction.HORIZ_FORWARD) # 页面水平右翻
    d.swipe_ext(Direction.HORIZ_BACKWARD) # 页面水平左翻
    ```

* 拖动

    ```python
    d.drag(sx, sy, ex, ey)
    d.drag(sx, sy, ex, ey, 0.5) # 拖动 0.5 秒（默认）
    ```

* 滑动多个点

    ```python
    # 从点 (x0, y0) 滑动到 (x1, y1)，然后到 (x2, y2)
    # 每两个点之间的时间间隔为 0.2 秒
    d.swipe_points([(x0, y0), (x1, y1), (x2, y2)], 0.2)
    ```

    这通常用于九宫格解锁，可以提前获取每个点的相对坐标（支持百分比），
    更详细的使用参考此帖子：[使用 u2 实现九宫图案解锁](https://testerhome.com/topics/11034)

* 触摸和拖动（Beta）

    这个接口属于比较底层的原始接口，虽然不完善，但能勉强使用。注：此处不支持百分比

    ```python
    d.touch.down(10, 10) # 模拟按下
    time.sleep(.01) # down 和 move 之间的延迟，自己控制
    d.touch.move(15, 15) # 模拟移动
    d.touch.up(10, 10) # 模拟抬起
    ```

注意：点击、滑动、拖动操作支持百分比位置值。例如：

`d.long_click(0.5, 0.5)` 表示长按屏幕中心。

### 屏幕相关操作

* 获取/设置设备方向

    可能的方向值：

    - `natural` 或 `n`
    - `left` 或 `l`
    - `right` 或 `r`
    - `upsidedown` 或 `u`（无法设置）

    ```python
    # 获取当前方向。输出值可能为 "natural"、"left"、"right" 或 "upsidedown"
    orientation = d.orientation

    # 警告：在我的 TT-M1 上未通过测试
    # 设置方向并锁定旋转
    # 注：设置 "upsidedown" 需要 Android >= 4.3。
    d.set_orientation('l') # 或 "left"
    d.set_orientation("l") # 或 "left"
    d.set_orientation("r") # 或 "right"
    d.set_orientation("n") # 或 "natural"
    ```

* 冻结/取消冻结旋转

    ```python
    # 冻结旋转
    d.freeze_rotation()
    # 取消冻结旋转
    d.freeze_rotation(False)
    ```

* 截屏

    ```python
    # 截屏并保存到计算机的文件，要求 Android >= 4.2。
    d.screenshot("home.jpg")
    
    # 获取 PIL.Image 格式的图片。需要安装 pillow 库
    image = d.screenshot() # 默认格式="pillow"
    image.save("home.jpg") # 或 home.png。目前只支持 png 和 jpg 格式

    # 获取 opencv 格式的图片。需要安装 numpy 和 cv2 库
    import cv2
    image = d.screenshot(format='opencv')
    cv2.imwrite('home.jpg', image)

    # 获取原始的 jpeg 数据
    imagebin = d.screenshot(format='raw')
    open("some.jpg", "wb").write(imagebin)
    ```

* 导出 UI 层次结构

    ```python
    # 获取 UI 层次结构的 dump 内容
    xml = d.dump_hierarchy()

    # compressed=True: 包括非导入节点
    # pretty: 格式化 xml
    # max_depth: 限制 xml 深度，默认为 50
    xml = d.dump_hierarchy(compressed=False, pretty=False, max_depth=50)
    ```

* 打开通知或快捷设置

    ```python
    d.open_notification()
    d.open_quick_settings()
    ```



### 选择器（Selector）

选择器是一个用于标识当前窗口中特定 UI 对象的便捷机制。

```python
# 选择文本为 'Clock' 且 className 为 'android.widget.TextView' 的对象
d(text='Clock', className='android.widget.TextView')
```

选择器支持以下参数。详细信息请参见 [UiSelector Java 文档](http://developer.android.com/tools/help/uiautomator/UiSelector.html)。

* `text`，`textContains`，`textMatches`，`textStartsWith`
* `className`，`classNameMatches`
* `description`，`descriptionContains`，`descriptionMatches`，`descriptionStartsWith`
* `checkable`，`checked`，`clickable`，`longClickable`
* `scrollable`，`enabled`，`focusable`，`focused`，`selected`
* `packageName`，`packageNameMatches`
* `resourceId`，`resourceIdMatches`
* `index`，`instance`

#### 子元素和兄弟元素

* 子元素

  ```python
  # 获取子元素或孙元素
  d(className="android.widget.ListView").child(text="Bluetooth")
  ```

* 兄弟元素

  ```python
  # 获取兄弟元素
  d(text="Google").sibling(className="android.widget.ImageView")
  ```

* 通过文本、描述或实例获取子元素

  ```python
  # 获取 className 为 "android.widget.LinearLayout" 的子元素
  # 以及其子元素或孙元素，文本为 "Bluetooth"
  d(className="android.widget.ListView", resourceId="android:id/list") \
    .child_by_text("Bluetooth", className="android.widget.LinearLayout")

  # 允许滚动搜索的子元素
  d(className="android.widget.ListView", resourceId="android:id/list") \
    .child_by_text(
       "Bluetooth",
       allow_scroll_search=True,
       className="android.widget.LinearLayout"
     )
  ```

  - `child_by_description` 用于查找孙元素具有指定描述的子元素，其他参数与 `child_by_text` 类似。
  
  - `child_by_instance` 用于查找具有指定实例的子元素，实例在其子层级的任何位置。此操作在可见视图上执行 **不进行滚动**。

  查看以下链接获取详细信息：

  - [UiScrollable](http://developer.android.com/tools/help/uiautomator/UiScrollable.html)，`getChildByDescription`，`getChildByText`，`getChildByInstance`
  - [UiCollection](http://developer.android.com/tools/help/uiautomator/UiCollection.html)，`getChildByDescription`，`getChildByText`，`getChildByInstance`

  上述方法支持链式调用，例如以下层次结构：

  ```xml
  <node index="0" text="" resource-id="android:id/list" class="android.widget.ListView" ...>
    <node index="0" text="WIRELESS & NETWORKS" resource-id="" class="android.widget.TextView" .../>
    <node index="1" text="" resource-id="" class="android.widget.LinearLayout" ...>
      <node index="1" text="" resource-id="" class="android.widget.RelativeLayout" ...>
        <node index="0" text="Wi‑Fi" resource-id="android:id/title" class="android.widget.TextView" .../>
      </node>
      <node index="2" text="ON" resource-id="com.android.settings:id/switchWidget" class="android.widget.Switch" .../>
    </node>
    ...
  </node>
  ```
  ![settings](https://raw.github.com/xiaocong/uiautomator/master/docs/img/settings.png)

  为了点击与文本 "Wi‑Fi" 右侧的开关小部件，我们首先需要选择开关小部件。然而，根据 UI 层次结构，存在多个几乎相同的开关小部件，仅通过 className 选择无法解决。另一种选择策略如下：

  ```python
  d(className="android.widget.ListView", resourceId="android:id/list") \
    .child_by_text("Wi‑Fi", className="android.widget.LinearLayout") \
    .child(className="android.widget.Switch") \
    .click()
  ```

* 相对定位

  我们还可以使用相对定位方法来获取视图：`left`，`right`，`top`，`bottom`。

  - `d(A).left(B)`，选择 A 左侧的 B。
  - `d(A).right(B)`，选择 A 右侧的 B。
  - `d(A).up(B)`，选择 A 上方的 B。
  - `d(A).down(B)`，选择 A 下方的 B。

  因此，对于上述情况，我们可以选择：

  ```python
  ## 选择 "Wi‑Fi" 右侧的 "switch"
  d(text="Wi‑Fi").right(className="android.widget.Switch").click()
  ```

* 多个实例

  有时屏幕上可能包含多个具有相同属性的视图，例如文本，您必须使用选择器中的 "instance" 属性来选择符合条件的实例，如下所示：

  ```python
  d(text="Add new", instance=0)  # 表示选择文本为 "Add new" 的第一个实例
  ```

  此外，uiautomator2 提供了类似 jQuery 的 API：

  ```python
  # 获取当前屏幕上具有文本 "Add new" 的视图数量
  d(text="Add new").count

  # 等同于 count 属性
  len(d(text="Add new"))

  # 通过索引获取实例
  d(text="Add new")[0]
  d(text="Add new")[1]
  ...

  # 迭代器
  for view in d(text="Add new"):
      view.info  # ...
  ```

  **注意**：当使用选择器遍历结果列表时，必须确保屏幕上的 UI 元素保持不变。否则，在遍历列表时可能会发生 "Element-Not-Found" 错误。

#### 获取已选择的 UI 对象状态及其信息

* 检查特定 UI 对象是否存在

    ```python
    d(text="Settings").exists  # 如果存在则返回 True，否则返回 False
    d.exists(text="Settings")  # 与上述属性等效。

    # 高级用法
    d(text="Settings").exists(timeout=3)  # 等待 3 秒，检查 "Settings" 是否出现，等同于 .wait(3)
    ```

* 获取特定 UI 对象的信息

    ```python
    d(text="Settings").info
    ```

    以下是可能的输出：

    ```
    { u'contentDescription': u'',
    u'checked': False,
    u'scrollable': False,
    u'text': u'Settings',
    u'packageName': u'com.android.launcher',
    u'selected': False,
    u'enabled': True,
    u'bounds': {u'top': 385,
                u'right': 360,
                u'bottom': 585,
                u'left': 200},
    u'className': u'android.widget.TextView',
    u'focused': False,
    u'focusable': True,
    u'clickable': True,
    u'chileCount': 0,
    u'longClickable': True,
    u'visibleBounds': {u'top': 385,
                        u'right': 360,
                        u'bottom': 585,
                        u'left': 200},
    u'checkable': False
    }
    ```

* 获取/设置/清除可编辑字段（例如，EditText 小部件）的文本

    ```python
    d(text="Settings").get_text()  # 获取小部件文本
    d(text="Settings").set_text("My text...")  # 设置文本
    d(text="Settings").clear_text()  # 清除文本
    ```

* 获取小部件的中心点

    ```python
    x, y = d(text="Settings").center()
    # x, y = d(text="Settings").center(offset=(0, 0)) # 左上角的 x, y
    ```

* 截取小部件的截图

    ```python
    im = d(text="Settings").screenshot()
    im.save("settings.jpg")
    ```

#### 对选定的 UI 对象执行点击操作
* 对特定对象执行点击

    ```python
    # 点击特定 UI 对象的中心
    d(text="Settings").click()
    
    # 等待元素最多 10 秒钟出现，然后点击
    d(text="Settings").click(timeout=10)
    
    # 带偏移量的点击（x_offset, y_offset）
    # click_x = x_offset * width + x_left_top
    # click_y = y_offset * height + y_left_top
    d(text="Settings").click(offset=(0.5, 0.5))  # 默认点击中心
    d(text="Settings").click(offset=(0, 0))  # 点击左上角
    d(text="Settings").click(offset=(1, 1))  # 点击右下角

    # 等待最多 10 秒，直到元素出现，默认超时为 0 秒
    clicked = d(text='Skip').click_exists(timeout=10.0)
    
    # 点击直到元素消失，返回布尔值
    is_gone = d(text="Skip").click_gone(maxretry=10, interval=1.0)  # maxretry 默认值为 10，interval 默认值为 1.0
    ```

* 对特定 UI 对象执行长按点击

    ```python
    # 对特定 UI 对象的中心执行长按
    d(text="Settings").long_click()
    ```

#### 对特定 UI 对象执行手势操作
* 将 UI 对象拖动到另一个点或另一个 UI 对象

    ```python
    # 注意：Android < 4.3 不支持 drag 操作
    # 将 UI 对象拖动到屏幕点 (x, y)，持续 0.5 秒
    d(text="Settings").drag_to(x, y, duration=0.5)
    # 将 UI 对象拖动到另一个 UI 对象的中心，持续 0.25 秒
    d(text="Settings").drag_to(text="Clock", duration=0.25)
    ```

* 从 UI 对象的中心向其边缘滑动

    滑动支持 4 个方向：

    - left
    - right
    - top
    - bottom

    ```python
    d(text="Settings").swipe("right")
    d(text="Settings").swipe("left", steps=10)
    d(text="Settings").swipe("up", steps=20)  # 1 步大约 5 毫秒，所以 20 步大约 0.1 秒
    d(text="Settings").swipe("down", steps=20)
    ```

* 从一个点到另一个点的双点手势

  ```python
  d(text="Settings").gesture((sx1, sy1), (sx2, sy2), (ex1, ey1), (ex2, ey2))
  ```

* 对特定 UI 对象执行双点手势

  支持两种手势：
  - `In`：从边缘到中心
  - `Out`：从中心到边缘

  ```python
  # 注意：直到 Android 4.3 才支持 pinch 操作
  # 从边缘到中心，这里是 "In" 不是 "in"
  d(text="Settings").pinch_in(percent=100, steps=10)
  # 从中心到边缘
  d(text="Settings").pinch_out()
  ```

* 等待特定 UI 出现或消失

    ```python
    # 等待 UI 对象出现
    d(text="Settings").wait(timeout=3.0)  # 返回布尔值
    # 等待 UI 对象消失
    d(text="Settings").wait_gone(timeout=1.0)
    ```

    默认超时为 20 秒。更多细节请查看 **全局设置**。

* 对特定 UI 对象（可滚动的）执行滚动操作

  可用属性：
  - `horiz` 或 `vert`
  - `forward` 或 `backward` 或 `toBeginning` 或 `toEnd`

  ```python
  # 默认垂直滚动向前（默认）
  d(scrollable=True).fling()
  # 向前水平滚动
  d(scrollable=True).fling.horiz.forward()
  # 向后垂直滚动
  d(scrollable=True).fling.vert.backward()
  # 水平滚动到开始
  d(scrollable=True).fling.horiz.toBeginning(max_swipes=1000)
  # 垂直滚动到结束
  d(scrollable=True).fling.toEnd()
  ```

* 对特定 UI 对象（可滚动的）执行滚动操作

  可用属性：
  - `horiz` 或 `vert`
  - `forward` 或 `backward` 或 `toBeginning` 或 `toEnd`，或 `to`

  ```python
  # 默认垂直滚动向前（默认）
  d(scrollable=True).scroll(steps=10)
  # 水平滚动向前
  d(scrollable=True).scroll.horiz.forward(steps=100)
  # 垂直滚动向后
  d(scrollable=True).scroll.vert.backward()
  # 水平滚动到开始
  d(scrollable=True).scroll.horiz.toBeginning(steps=100, max_swipes=1000)
  # 垂直滚动到结束
  d(scrollable=True).scroll.toEnd()
  # 垂直滚动直到特定 UI 对象出现
  d(scrollable=True).scroll.to(text="Security")
  ```

### WatchContext
目前的 `watch_context` 是通过 threading 启动的，每 2 秒检查一次。当前只支持点击操作。

```python
with d.watch_context() as ctx:
    # 当同时出现 （立即下载 或 立即更新）和 取消 按钮时，点击取消
    ctx.when("^立即(下载|更新)").when("取消").click() 
    ctx.when("同意").click()
    ctx.when("确定").click()
    # 上面三行代码是立即执行的，不会有等待
    
    ctx.wait_stable()  # 开启弹窗监控，并等待界面稳定（两个弹窗检查周期内没有弹窗代表稳定）

    # 使用 call 函数触发函数回调
    # call 支持两个参数，d 和 el，不区分参数位置，可以不传参，如果传参变量名不能写错
    # eg: 当有元素匹配 "仲夏之夜"，点击返回按钮
    ctx.when("仲夏之夜").call(lambda d: d.press("back"))
    ctx.when("确定").call(lambda el: el.click())

    # 其他操作

# 为了方便，也可以使用代码中默认的弹窗监控逻辑
# 下面是目前内置的默认逻辑，可以加群 at 群主，增加新的逻辑，或者直接提 pr
    # when("继续使用").click()
    # when("移入管控").when("取消").click()
    # when("^立即(下载|更新)").when("取消").click()
    # when("同意").click()
    # when("^(好的|确定)").click()
with d.watch_context(builtin=True) as ctx:
    # 在已有的基础上增加
    ctx.when("@tb:id/jview_view").when('//*[@content-desc="图片"]').click()

    # 其他脚本逻辑
```

另一种写法：

```python
ctx = d.watch_context()
ctx.when("设置").click()
ctx.wait_stable()  # 等待界面不再有弹窗

ctx.close()
```  


### Watcher
**推荐使用 WatchContext，写法更加简洁。**

~~您可以注册 [watchers](http://developer.android.com/tools/help/uiautomator/UiWatcher.html) 来在没有找到匹配的选择器时执行某些操作。~~

在 2.0.0 之前，使用的是 uiautomator-jar 库中的 [Watcher](http://developer.android.com/tools/help/uiautomator/UiWatcher.html) 方法，但在实践中发现，如果 uiautomator 连接失败并重启，所有的 watcher 配置都会丢失，这显然是不可接受的。

因此，目前采用了后台线程的方法（依赖 threading 库），每隔一段时间 dump 一次 hierarchy，当匹配到元素时执行相应的操作。

#### 用法示例

注册监控：

```python
# 常用写法，注册匿名监控
d.watcher.when("安装").click()

# 注册名为 ANR 的监控，当出现 ANR 和 Force Close 时，点击 Force Close
d.watcher("ANR").when(xpath="ANR").when("Force Close").click()

# 其他回调示例
d.watcher.when("抢红包").press("back")
d.watcher.when("//*[@text = 'Out of memory']").call(lambda d: d.shell('am force-stop com.im.qq'))

# 回调示例
def click_callback(d: u2.Device):
    d.xpath("确定").click()  # 在回调中调用不会再次触发 watcher

d.xpath("继续").click()  # 使用 d.xpath 检查元素时，会触发 watcher（最多触发 5 次）

# 开始后台监控
d.watcher.start()
```

监控操作：

```python
# 移除 ANR 的监控
d.watcher.remove("ANR")

# 移除所有的监控
d.watcher.remove()

# 开始后台监控
d.watcher.start()
d.watcher.start(2.0)  # 默认监控间隔为 2.0s

# 强制运行所有监控
d.watcher.run()

# 停止监控
d.watcher.stop()

# 停止并移除所有的监控，常用于初始化
d.watcher.reset()
```

更多文档内容可以参考源码 [watcher.py](uiautomator2/watcher.py)。

### Global Settings

```python
u2.HTTP_TIMEOUT = 60  # 默认值为 60s，HTTP 默认请求超时时间
```

其他配置项目前已大部分集中在 `d.settings` 中，根据后期需求可能会有增减。

```python
print(d.settings)
{'operation_delay': (0, 0),
 'operation_delay_methods': ['click', 'swipe'],
 'wait_timeout': 20.0}

# 配置点击前延时 0.5s，点击后延时 1s
d.settings['operation_delay'] = (.5, 1)

# 修改延迟生效的方法
# 其中 double_click, long_click 都对应 click
d.settings['operation_delay_methods'] = ['click', 'swipe', 'drag', 'press']
d.settings['wait_timeout'] = 20.0  # 默认控件等待时间（原生操作，xpath 插件的等待时间）

d.settings['max_depth'] = 50  # 默认 50，限制 dump_hierarchy 返回的元素层级
```

对于版本升级中设置过期的配置，会提示 **Deprecated**，但不会抛出异常。

```bash
>>> d.settings['click_before_delay'] = 1  
[W 200514 14:55:59 settings:72] d.settings[click_before_delay] deprecated: Use operation_delay instead
```

#### **UiAutomator 恢复方式设置**

在安卓设备中，实际上安装了两个 APK，一个是前台可见的小黄车，另一个包名为 `com.github.uiautomator.test` 在后台不可见。二者使用相同的证书签名。

不可见的应用实际上是一个测试包，包含有所有的测试代码，核心的测试服务也是通过该包启动的。然而系统需要小黄车一直在后台运行。若小黄车应用被杀，后台服务也会被快速终止。为此，目前通过 `am startservice` 启动后台服务，但这仍然是一个不可解决的问题。

~~通过 `d.settings["uiautomator_runtest_app_background"] = True` 可以调整该行为。True 代表启动应用，False 代表启动服务。~~

#### **UiAutomator 中的超时设置（隐藏方法）**

```python
>> d.jsonrpc.getConfigurator() 
{'actionAcknowledgmentTimeout': 500,
 'keyInjectionDelay': 0,
 'scrollAcknowledgmentTimeout': 200,
 'waitForIdleTimeout': 0,
 'waitForSelectorTimeout': 0}

>> d.jsonrpc.setConfigurator({"waitForIdleTimeout": 100})
{'actionAcknowledgmentTimeout': 500,
 'keyInjectionDelay': 0,
 'scrollAcknowledgmentTimeout': 200,
 'waitForIdleTimeout': 100,
 'waitForSelectorTimeout': 0}
```

为了防止客户端程序响应超时，`waitForIdleTimeout` 和 `waitForSelectorTimeout` 已改为 0。

更多参考：[Google uiautomator Configurator](https://developer.android.com/reference/android/support/test/uiautomator/Configurator)

### Input Method
此方法通常用于在无法直接获取控件时进行输入。

```python
# 采用剪贴板粘贴方式输入
d.send_keys("你好123abcEFG")
d.send_keys("你好123abcEFG", clear=True)

d.clear_text()  # 清除输入框中的所有内容

d.send_action()  # 根据输入框的需求，自动执行回车、搜索等指令，已在版本 3.1 中添加
# 也可以指定发送的输入法动作，例如：d.send_action("search")，支持 go, search, send, next, done, previous
```

```python
print(d.current_ime())  # 获取当前输入法 ID
```

> 更多参考：[IME_ACTION_CODE](https://developer.android.com/reference/android/view/inputmethod/EditorInfo)

### Toast

```python
print(d.last_toast)  # 获取最后一个 toast，如果没有则返回 None
d.clear_toast()  # 清除 toast
```

> 已在版本 3.2.0 中修复。

### XPath

Java 中的 uiautomator 默认不支持 XPath，这里做了扩展，但速度可能会稍慢。

例如，对于一个节点的内容：

```xml
<android.widget.TextView
  index="2"
  text="05:19"
  resource-id="com.netease.cloudmusic:id/qf"
  package="com.netease.cloudmusic"
  content-desc=""
  checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false"
  scrollable="false" long-clickable="false" password="false" selected="false" visible-to-user="true"
  bounds="[957,1602][1020,1636]" />
```

XPath 定位和使用方法：

一些属性名可能已修改，请注意：

- `description` -> `content-desc`
- `resourceId` -> `resource-id`

常见用法：

```python
# 等待元素存在 10 秒
d.xpath("//android.widget.TextView").wait(10.0)

# 查找并点击
d.xpath("//*[@content-desc='分享']").click()

# 检查是否存在
if d.xpath("//android.widget.TextView[contains(@text, 'Se')]").exists:
    print("存在")

# 获取所有 TextView 的文本、属性和中心点
for elem in d.xpath("//android.widget.TextView").all():
    print("Text:", elem.text)
    # 属性字典
    # {'index': '1', 'text': '999+', 'resource-id': 'com.netease.cloudmusic:id/qb', ...}
    print("Attrib:", elem.attrib)
    # 坐标 (100, 200)
    print("Position:", elem.center())
```

查看 [其他 XPath 常见用法](XPATH.md)。


### Screenrecord (Deprecated)
视频录制功能已废弃，推荐使用 [scrcpy](https://github.com/Genymobile/scrcpy) 来代替。

此功能并未使用手机自带的 `screenrecord` 命令，而是通过获取手机图片合成视频的方法实现，因此需要安装额外的依赖，如 `imageio`, `imageio-ffmpeg`, `numpy` 等。由于某些依赖较大，建议通过镜像安装。

可以运行以下命令进行安装：

```bash
pip3 install -U "uiautomator2[image]" -i https://pypi.doubanio.com/simple
```

#### 使用方法

```python
d.screenrecord('output.mp4')

time.sleep(10)
# 或执行其他操作

d.screenrecord.stop()  # 停止录制后，output.mp4 文件才能打开
```

录制时可以指定 `fps`（当前默认为 20），这个值低于 `minicap` 输出图片的速度，因此不建议修改。

---

### Enable uiautomator2 Logger

为了启用日志输出，可以使用以下两种方法：

```python
from uiautomator2 import enable_pretty_logging
enable_pretty_logging()
```

或者：

```python
import logging
logger = logging.getLogger("uiautomator2")
# 设置日志配置
```

---

### Stop UiAutomator

当 Python 程序退出时，UiAutomator 会自动退出。您也可以通过接口手动停止服务：

```python
d.stop_uiautomator()
```

---

### Google UiAutomator 2.0 和 1.x 的区别

1. **新增接口**：UiObject2、Until、By、BySelector
2. **引入方式**：2.0 中，`com.android.uiautomator.core.*` 被废弃，改为 `android.support.test.uiautomator`
3. **构建系统**：1.x 使用 Maven 和/或 Ant；2.0 使用 Gradle
4. **生成的测试包形式**：1.x 为 zip/jar，2.0 为 apk
5. **在本地环境执行 UIAutomator 测试的启动方式**：
   - 1.x：`adb shell uiautomator runtest UiTest.jar -c package.name.ClassName`
   - 2.0：`adb shell am instrument -e class com.example.app.MyTest com.example.app.test/android.support.test.runner.AndroidJUnitRunner`
6. **支持 Android 服务及接口**：1.x 不支持，2.0 支持
7. **日志输出**：1.x 使用 `System.out.print` 输出，2.0 输出至 Logcat
8. **执行方式**：
   - 1.x：测试用例需继承 `UiAutomatorTestCase`，测试方法必须以 `test` 开头
   - 2.0：测试方法无需继承任何父类，使用注解进行标记

---

### 依赖项目

- [uiautomator jsonrpc server](https://github.com/openatx/android-uiautomator-server/)
- ~~uiautomator 守护程序~~ [atx-agent](https://github.com/openatx/atx-agent)（已废弃）

---

### Contributors

- [codeskyblue](https://github.com/codeskyblue)
- [xiaocong](https://github.com/xiaocong)
- [yuanyuan](https://github.com/yuanyuan)
- [QianJin2013](https://github.com/QianJin2013)
- [xiscoxu](https://github.com/xiscoxu)
- [mingyuan-xia](https://github.com/mingyuan-xia)
- [artikz](https://github.com/artikz)

更多 [贡献者](../../graphs/contributors)

---

### 其他优秀的项目

- [awesome-test-automation](https://github.com/atinfo/awesome-test-automation)：所有优秀测试框架的集合
- [google/mobly](https://github.com/google/mobly)：谷歌内部的测试框架，虽然我不太懂，但感觉很好用
- [Maxim](https://github.com/zhangzhao4444/Maxim)：基于 Uiautomator 的 Monkey 测试工具
- [SikuliX](http://www.sikulix.com/)：基于图像识别的自动化测试框架
- [Airtest](http://airtest.netease.com/)：本项目的前身，网易广州团队接手并继续优化

---

### LICENSE

[MIT](LICENSE)