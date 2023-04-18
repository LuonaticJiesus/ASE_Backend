## 1 数据库

==要不，在Post添加`点赞数`、`是否加精`和`收藏数`属性，Comment数据类型中添加`点赞数`属性？==

### UserLogin

| 属性名  | 类型         | 限制           |
| ------- | ------------ | -------------- |
| user_id | integerField |                |
| token   | CharField    | max_length=200 |



### UserInfo

主键：user_id

| 属性名   | 类型      | 限制                | 说明 |
| -------- | --------- | ------------------- | ---- |
| user_id  | AutoField |                     |      |
| name     | CharField | max_length=200      |      |
| password | CharField | max_length=200      |      |
| card_id  | CharField | max_length=200      | 学号 |
| phone    | CharField | max_length=20，可空 |      |
| email    | CharField | max_length=50，可空 |      |



### Post

主键：post_id

| 属性名   | 类型          | 限制           | 说明     |
| -------- | ------------- | -------------- | -------- |
| post_id  | AutoField     |                |          |
| title    | CharField     | max_length=200 |          |
| user_id  | IntegerField  |                | 外键     |
| txt      | TextField     |                |          |
| block_id | IntegerField  |                | 外键     |
| time     | DateTimeField |                | 发布时间 |

帖子Post与发布人user_id和课程模块block相关联



### PostLike

点赞帖子

主键：user_id, post_id

| 属性名  | 类型         | 限制 | 说明 |
| ------- | ------------ | ---- | ---- |
| user_id | IntegerField |      |      |
| post_id | IntegerField |      |      |



### PostFavor

收藏帖子

主键：user_id, post_id

| 属性名  | 类型         | 限制 | 说明 |
| ------- | ------------ | ---- | ---- |
| user_id | IntegerField |      |      |
| post_id | IntegerField |      |      |



### PostChosen

主键：post_id, block_id

| 属性名   | 类型         | 限制 | 说明 |
| -------- | ------------ | ---- | ---- |
| post_id  | IntegerField |      |      |
| block_id | IntegerField |      |      |



### Block

模块

主键：block_id

| 属性名             | 类型          | 限制           | 说明                                                         |
| ------------------ | ------------- | -------------- | ------------------------------------------------------------ |
| block_id           | AutoField     |                |                                                              |
| name               | CharField     | max_length=200 |                                                              |
| time               | DateTimeField |                | 模块建立的时间                                               |
| approve_permission | IntegerField  |                | 访问block的权限设置<br /><0: 无需认证，0:需要路人认证，1:成员认证，2:助理认证，3:管理认证，>=4：超管认证 |



### Comment

主键：comment_id

| 属性名     | 类型          | 限制 | 说明                 |
| ---------- | ------------- | ---- | -------------------- |
| comment_id | AutoField     |      |                      |
| user_id    | IntegerField  |      | 发表评论的用户id     |
| post_id    | IntegerField  |      | 评论所在帖子id       |
| parent_id  | IntegerField  | 可空 | 评论所回复的父级评论 |
| txt        | TextField     |      |                      |
| time       | DateTimeField |      | 帖子发布时间         |



### CommentLike

主键：user_id, comment_id

| 属性名     | 类型         | 限制 | 说明 |
| ---------- | ------------ | ---- | ---- |
| user_id    | IntegerField |      |      |
| comment_id | IntegerField |      |      |



### Notice

主键：notice_id

| 属性名    | 类型          | 限制           | 说明             |
| --------- | ------------- | -------------- | ---------------- |
| notice_id | AutoField     |                |                  |
| title     | CharField     | max_length=200 |                  |
| txt       | TextField     |                |                  |
| user_id   | IntegerField  |                | 发布通知的用户id |
| block_id  | IntegerField  |                | 通知所属模块id   |
| time      | DateTimeField |                | 发布通知的时间   |
| ddl       | DateTimeField |                | 截止时间         |



### NoticeConfirm

主键：user_id, notice_id

| 属性名    | 类型         | 限制 | 说明 |
| --------- | ------------ | ---- | ---- |
| user_id   | IntegerField |      |      |
| notice_id | IntegerField |      |      |



### Permission

主键：user_id, block_id

| 属性名     | 类型         | 限制 | 说明               |
| ---------- | ------------ | ---- | ------------------ |
| user_id    | IntegerField |      |                    |
| block_id   | IntegerField |      | 用户订阅的模块id   |
| permission | IntegerField |      | 用户对该模块的权限 |



### Contribution

主键：user_id, block_id

| 属性名       | 类型         | 限制 | 说明 |
| ------------ | ------------ | ---- | ---- |
| user_id      | IntegerField |      |      |
| block_id     | IntegerField |      |      |
| contribution | IntegerField |      |      |



### Message

主键：message_id

| 属性名      | 类型          | 限制                  | 说明                                                         |
| ----------- | ------------- | --------------------- | ------------------------------------------------------------ |
| message_id  | AutoField     |                       |                                                              |
| sender_id   | IntegerField  |                       | 发送/产生消息的用户                                          |
| receiver_id | IntegerField  |                       | 接受消息的用户                                               |
| content     | CharField     | max_length=200        | 消息的内容（"\[用户名\]{特殊身份} \[点赞/加精/回复/删除\] 了您的 [帖子，评论]!") |
| source_type | IntegerField  | (1: Post, 2: Comment) | 消息来源                                                     |
| source_id   | IntegerField  |                       | 消息来源的id                                                 |
| time        | DateTimeField |                       | 消息产生的时间                                               |
| status      | IntegerField  | (0:未查看, 1:已查看)  | 消息状态                                                     |



## 2 功能函数

### `four_s_block.py`

| 函数名                 | 传入参数                                                     | 返回值 | 功能（考虑贡献值）                                           | 前置条件（权限等） | 异常处理 | 接口路由                 | 请求类型 |
| ---------------------- | ------------------------------------------------------------ | ------ | ------------------------------------------------------------ | ------------------ | -------- | ------------------------ | -------- |
| block_query_all        |                                                              |        | 查询所有模块信息                                             |                    |          | `block/queryAll/`        | GET      |
| block_query_permission | user_id<br />permission                                      |        |                                                              |                    |          | `block/queryPermission/` | GET      |
| block_subscribe        | user_id(request.META自带)<br />block_id<br />subscribe(0:取消订阅) |        | subscribe=0:取消订阅<br />subscribe非0:订阅，`update_perm = 1 if block_perm < 0 else 0` |                    |          | `block/subscribe/`       | POST     |



### `four_s_comment.py`

| 函数名            | 传入参数                                                     | 返回值           | 功能（考虑贡献值）                                           | 前置条件（权限等）                               | 异常处理                                                     | 接口路由             | 请求类型       |
| ----------------- | ------------------------------------------------------------ | ---------------- | ------------------------------------------------------------ | ------------------------------------------------ | ------------------------------------------------------------ | -------------------- | -------------- |
| wrap_comment      | 一条comment数据项<br />用户id                                | 包装好的字典数据 | 封装数据：comment数据+like_cnt+user_name+like_state          |                                                  |                                                              |                      | 不属于接口函数 |
| comment_queryPost | user_id(request.META自带)<br />post_id                       |                  | 查询某个post下的所有的评论                                   |                                                  | post不存在                                                   | `comment/queryPost/` | GET            |
| comment_publish   | user_id(request.META自带)<br />post_id<br />parent_id<br />txt |                  | 发布评论                                                     |                                                  | post不存在<br />parent_id不为空但父级comment不存在<br />父级comment的post_id与当前post_id不一致<br />用户没有在当前block下发布评论的权限<br />==用户没有足够的point发布评论== | `comment/publish/`   | POST           |
| comment_delete    | user_id(request.META自带)<br />comment_id                    |                  | 删除评论，==其子评论保留？==                                 | - 删除自己的评论<br />- 删除他人的评论，perm >=2 | 评论不存在<br />==删除他人评论时，==权限不足(pem<2)<br />~可删除自己发布的评论~ | `comment/delete/`    | POST           |
| comment_like      | user_id(request.META自带)<br />comment_id<br />like(0:取消点赞) |                  | like=0:取消点赞<br />like!=0:点赞<br />==没有设置成原子操作== |                                                  | 评论不存在<br />                                             | `comment/like/`      | POST           |



### `four_s_notice.py`

| 函数名             | 传入参数                                                     | 返回值 | 功能（考虑贡献值）                                           | 前置条件（权限等）                      | 异常处理                      | 接口路由             | 请求类型 |
| ------------------ | ------------------------------------------------------------ | ------ | ------------------------------------------------------------ | --------------------------------------- | ----------------------------- | -------------------- | -------- |
| notice_query_recv  | user_id<br />show_confirm(0:查询未"确认收到"的通知, 非0:所有通知)<br />undue_op(0:所有通知; >0:未截止通知; <0:已截止通知) |        | 查询收到的(所有；未截止；已截止）(所有; 未确认)的通知信息<br /> |                                         |                               | `notice/queryRecv/`  | GET      |
| notice_query_send  | user_id                                                      |        | 查询用户发送的所有通知，按时间排序                           | ==用户的permission>=2==                 | 用户不存在                    | `notice/querySend/`  | GET      |
| notice_query_block | block_id                                                     |        | 查询block下的所有通知，按时间排序                            |                                         | block不存在                   | `notice/queryBlock/` | GET      |
| notice_publish     | user_id(request.META自带)<br />title<br />txt<br />block_id<br />time<br />ddl |        | 发布通知                                                     | 用户权限>=2                             | 权限不够                      | `notice/publish/`    | POST     |
| notice_delete      | user_id(request.META自带)<br />notice_id                     |        | 删除通知                                                     | 用户权限perm>=2且删除的是自己发布的通知 | 权限不足:不是该用户发布的通知 | `notice/delete/`     | DELETE   |



### `four_s_message.py`

| 函数名              | 传入参数                                                     | 返回值 | 功能（考虑贡献值）     | 前置条件（权限等） | 异常处理 | 接口路由               | 请求类型 |
| ------------------- | ------------------------------------------------------------ | ------ | ---------------------- | ------------------ | -------- | ---------------------- | -------- |
| message_gen         | sender_id<br />receiver_id<br />content<br />source_type<br />source_id |        | 生成一条消息           |                    |          |                        | 内部函数 |
| message_query_all   | user_id(request.META自带)                                    |        | 查询登录用户的所有信息 | 用户已登录         |          | `message/queryRec/`    | GET      |
| message_confirm_all |                                                              |        | 所有消息设置为已读     | 用户已登录         |          | `message/confirm/`     | POST     |
| message_confirm     | message_id                                                   |        | 改变message.status为1  | 用户已登录         |          | `message/confirm_all/` | POST     |



### `four_s_permission.py`

| 函数名                | 传入参数                                                     | 返回值 | 功能（考虑贡献值）                               | 前置条件（权限等） | 异常处理                        | 接口路由                | 请求类型 |
| --------------------- | ------------------------------------------------------------ | ------ | ------------------------------------------------ | ------------------ | ------------------------------- | ----------------------- | -------- |
| permission_query_user | block_id<br />permission                                     |        | 查询权限等于permission的block_id下的所有用户信息 |                    |                                 | `permission/queryUser/` | GET      |
| permission_set        | user_id(request.META自带)<br />user_id<br />block_id<br />permission |        |                                                  |                    | 权限错误permission ![0,1,2,3,4] | `permission/set/`       | POST     |
|                       |                                                              |        |                                                  |                    |                                 |                         |          |



### `four_s_post.py`

==帖子加精的问题：可以直接在Post里面加一个属性isChosen，加精为1，非加精为0==

| 函数名            | 传入参数                                                     | 返回值           | 功能（考虑贡献值）                             | 前置条件（权限等）                               | 异常处理                    | 接口路由           | 请求类型 |
| ----------------- | ------------------------------------------------------------ | ---------------- | ---------------------------------------------- | ------------------------------------------------ | --------------------------- | ------------------ | -------- |
| wrap_post         | 一条post数据项<br />user_id                                  | 包装后的post信息 |                                                |                                                  |                             |                    |          |
| post_query_title  | user_id(request.META自带)<br />post_name                     |                  | 根据post_name查找post                          |                                                  |                             | `post/queryTitle/` | GET      |
| post_query_block  | user_id(request.META自带)<br />block_id                      |                  | 查询block下发布的所有帖子                      |                                                  |                             | `post/queryBlock/` | GET      |
| post_publish      | user_id(request.META自带)<br />title<br />txt<br />block_id  |                  | 发布帖子                                       | 用户在当前block下的权限>=1<br />                 | 权限不足<br />==point不足== | `post/queryUser/`  | POST     |
| post_delete       | user_id(request.META自带)<br />post_id                       |                  | 删除帖子，级联删除评论、加精、收藏、点赞的信息 | - 删除自己发布的帖子<br />- 删除他人帖子:perm>=2 | 权限不足                    | `post/publish/`    | POST     |
| post_like         | user_id(request.META自带)<br />post_id<br />like(0:取消点赞,非0:点赞) |                  | 点赞或取消点赞帖子                             | 用户在帖子所在的block下的perm>=1                 | 权限错误                    | `post/delete/`     | POST     |
| post_choose       | user_id(request.META自带)<br />post_id<br />chosen(0:取消加精,非0:加精) |                  | 加精或取消加精帖子                             | 用户在帖子所在的block下的perm>=2                 |                             | `post/like/`       |          |
| post_query_chosen |                                                              |                  |                                                |                                                  |                             | `post/choose/`     |          |



### `four_s_user.py`

| 函数名          | 传入参数                                                     | 返回值            | 功能（考虑贡献值） | 前置条件（权限等） | 异常处理                                           | 接口路由          | 请求类型 |
| --------------- | ------------------------------------------------------------ | ----------------- | ------------------ | ------------------ | -------------------------------------------------- | ----------------- | -------- |
| user_signup     | username<br />password<br />card_id(==可以为空吗？==)<br />phone(可空)<br />email(可空) |                   |                    |                    | 用户名或密码为空<br />用户名已存在<br />学号已存在 | `user/signup/`    | POST     |
| user_login      | username<br />password                                       | userid<br />token |                    |                    |                                                    | `user/login/`     | POST     |
| user_change_pwd | user_id(request.META自带)<br />new_pwd                       |                   |                    |                    |                                                    | `user/changePwd/` | POST     |