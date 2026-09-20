# 首次导入GitHub

## 实际状态与目标

本文件随仓库导入包准备。**准备这个包不等于已经创建GitHub仓库或上传成功。** 当前聊天连接已识别账号`1571379714-creator`，但所提供的GitHub工具没有创建仓库操作；本轮没有在远端写入任何文件。

默认目标名称：`flagship-era`；默认账号：`1571379714-creator`；默认可见性：**Private**。从5.0建立首次提交和`v5.0`标签，不改变游戏内容。这里不创建另外的GitHub Projects看板。

## 方法A：本机脚本创建并上传

需要本机已经安装Python 3、Git和GitHub CLI（命令`gh`）。Python只是运行上传脚本，不需要安装游戏排版依赖。GitHub登录在你的电脑和官方浏览器中进行，不要把密码或Token发到聊天。

工具官方入口：
- Git for Windows：<https://git-scm.com/install/windows>
- GitHub CLI：<https://cli.github.com/>

解压整个导入包到独立文件夹，不要直接在ZIP预览内运行，也不要解压进另一个已有Git仓库。

Windows可以双击根目录`publish-to-github.cmd`，也可以打开终端执行：

```powershell
py -3 tools/publish_github.py --execute
```

脚本会先核对全部原始5.0文件和导入清单，显示目标账号/仓库与私有设置，再要求输入`CREATE`确认。首次使用`gh`时会启动官方浏览器登录。必须登录上述目标账号，错账号会停止。

流程：验证文件 → 确认目标 → 本地登录 → 初始化本地main提交与v5.0标签 → 创建私有仓库 → 上传main及标签 → 核对远端提交和文件树。全部成功后才输出“上传并核验完成”。

如果只是检查文件，不想创建/登录/上传：

```powershell
py -3 tools/publish_github.py
```

已存在的同名仓库不会被覆盖。需要换名时在首次执行前指定：

```powershell
py -3 tools/publish_github.py --execute --name flagship-era-design
```

程序不会执行强推、删除、改公开、发布网站、邀请成员或添加开源许可。Git使用本次调用的CLI认证辅助，不改全局Git配置；本次初始提交使用目标账号的GitHub no-reply身份。中断后状态保存在`.publish-state.json`，它不上传。已有原包文件改变时校验会拒绝继续，以免初始快照被悄悄替换。

**本脚本在当前环境完成本地校验、语法与隔离测试，但没有在真实账户上执行仓库创建/推送；远端权限、网络与本机工具仍以实际执行结果为准。**

## 方法B：只用GitHub网页导入

不使用命令行时，可以先在GitHub新建一个Private仓库，名称`flagship-era`，再使用页面中的文件上传入口，将本包根目录下的文件与文件夹上传并提交。使用原有目录层级，不只上传ZIP本身。确保`.github`、`.gitignore`、`.gitattributes`等以点开头的项目文件也保留。

官方步骤：
- 新建仓库：<https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository>
- 上传文件：<https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository>

网页方法不会自动建立v5.0标签，也不会执行脚本里的远端文件树核验；请不要把它称为已通过脚本验证。上传后应检查README、`versions/5.0/work/v50_data.json`和各个PDF/HTML文件是否存在。

## 上传之后

把实际仓库地址作为后续协作入口。如果希望聊天中的GitHub连接读写这个新仓库，还需在GitHub应用授权中使它可访问该仓库；不要发送任何密钥。后续版本按`docs/workflow.md`推进，不再用首次创建工具覆盖既有项目。

## 脚本依据

归档准备日核对了GitHub CLI官方文档：
- `gh repo create`：<https://cli.github.com/manual/gh_repo_create>
- `gh auth login`：<https://cli.github.com/manual/gh_auth_login>
- Git认证配置：<https://cli.github.com/manual/gh_auth_setup-git>

GitHub CLI支持从本地仓库建立新远端，但这不表示当前聊天连接拥有同样的创建能力。脚本依赖的是你电脑上单独登录的GitHub CLI。
