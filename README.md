# Signal Bug Showcase Repo

## Installation

Install dependencies using UV package manager
```bash
uv sync
```

## Run

Launch the application using the entrypoint script:
```bash
./entrypoint.sh
```

It does the following:
- Apply migrations
- Createe a superuser
- Run the server

Note: If you have already created a superuser - press Ctrl+C to skip the superuser creation step.


## Reproducing the bug

1. Open the browser and navigate to `http://127.0.0.1:8000/admin/`
2. Login using the superuser credentials
3. Click on the "Groups" link
4. Click on the "Add group" button
5. Select any permissions (for example - "Can view log entry"), fill in the Group name and hit "Save" (or "Save and continue editing")
6. Check console logs, you should see something like:
```log
2025-02-27 15:22:04,721 [INFO] /workspaces/example/djangotutorial/mysite/utils.py:45 Security Event "{"action_flag": 1, "action_time": "datetime.datetime(2025, 2, 27, 15, 22, 4, 719269, tzinfo=datetime.timezone.utc)", "change_message": "[{\"added\": {}}]", "content_type": "<ContentType: Authentication and Authorization | group>", "kwargs": {"raw": false, "signal": "<django.db.models.signals.ModelSignal object at 0x7f9983f502c0>", "update_fields": null, "using": "default"}, "msg": "LogEntry 5 was created\n", "object_id": 3, "object_repr": "Test", "sender": "<class 'django.contrib.admin.models.LogEntry'>", "user": "<User: root>"}"
```
7. (Reopen the Group) hit "Delete" on the group you just created
8. Check console logs, but see no "Security Event" log
9. Check "Log entries" [page](http://127.0.0.1:8000/admin/admin/logentry/)
```log
2025-02-27 15:25:18,008 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /static/admin/css/widgets.css HTTP/1.1" 304 0"
2025-02-27 15:25:18,074 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /static/admin/img/icon-unknown.svg HTTP/1.1" 304 0"
2025-02-27 15:25:18,075 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /static/admin/img/selector-icons.svg HTTP/1.1" 304 0"
2025-02-27 15:25:18,075 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /static/admin/img/icon-unknown-alt.svg HTTP/1.1" 304 0"
2025-02-27 15:25:18,871 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /admin/auth/group/3/delete/ HTTP/1.1" 200 7806"
2025-02-27 15:25:18,928 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /static/admin/js/cancel.js HTTP/1.1" 200 884"
2025-02-27 15:25:19,894 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""POST /admin/auth/group/3/delete/ HTTP/1.1" 302 0"
2025-02-27 15:25:19,908 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /admin/auth/group/ HTTP/1.1" 200 8213"
2025-02-27 15:25:19,998 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /admin/jsi18n/ HTTP/1.1" 200 3342"
2025-02-27 15:25:20,024 [INFO] /workspaces/example/.venv/lib/python3.12/site-packages/django/core/servers/basehttp.py:213 ""GET /static/admin/img/icon-yes.svg HTTP/1.1" 304 0"
```
10. You should see both log entries - for Addition and Deletion.

## Expected behavior

The "Security Event" log should be printed for both Addition and Deletion of the group, since the same `post_save` signal is used for both actions.


## Debugging

You may want to place debug stops in the signal, or in the source code of Django LogEntry model to see what's happening.

_I've tried to no avail, the signal is not being called, but I can't tell why :shrug:_

## Environment

You can run this code in a devcontainer, either on your local machine or in a codespace.
Using a devcontainer you won't have to install UV package manager, but the rest of actions is identical.
