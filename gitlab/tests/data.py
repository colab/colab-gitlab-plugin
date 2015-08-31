colab_apps = {'gitlab':
              {'menu_title': None,
               'private_token': 'token',
               'upstream': 'localhost',
               'urls':
               {'include': 'colab.plugins.gitlab.urls',
                'namespace': 'gitlab',
                'prefix': 'gitlab/'}}}

projects_json = [{"id": 32,
                  "description": "Test Gitlab",
                  "default_branch": "master",
                  "public": True,
                  "archived": False,
                  "visibility_level": 20,
                  "ssh_url_to_repo": "git@localhost/gitlabhq.git",
                  "http_url_to_repo": "localhost/gitlabhq.git",
                  "web_url": "localhost/gitlabhq",
                  "name": "Gitlab",
                  "name_with_namespace": "Test / Gitlab",
                  "path": "gitlabhq"}]

groups_json = [{"id": 23,
                "name": "Group 1",
                "path": "group-1",
                "owner_id": None},
               {"id": 27,
                "name": "Group 2",
                "path": "group-2",
                "owner_id": None}]

merge_json = [{"id": 7,
               "iid": 1,
               "project_id": 14,
               "title": "Merge Title",
               "description": "description",
               "state": "merged",
               "created_at": "2014-10-24T12:05:55.659Z",
               "updated_at": "2014-10-24T12:06:15.572Z",
               "target_branch": "master",
               "source_branch": "settings_fix",
               "upvotes": 0,
               "downvotes": 0,
               "author": {"name": "user",
                          "username": "user",
                          "id": 8,
                          "state": "active",
                          "avatar_url": "localhost"},
               "assignee": {"name": "user",
                            "username": "user",
                            "id": 8,
                            "state": "active",
                            "avatar_url": "localhost"},
               "source_project_id": 14,
               "target_project_id": 14,
               "labels": [],
               "milestone": None}]

issues_json = [{"id": 8,
                "iid": 1,
                "project_id": 32,
                "title": "title",
                "description": "description",
                "state": "opened",
                "created_at": "2014-10-11T16:25:37.548Z",
                "updated_at": "2014-10-11T16:25:37.548Z",
                "labels": [],
                "milestone": None,
                "assignee": {"name": "name",
                             "username": "username",
                             "id": 2,
                             "state": "active",
                             "avatar_url": "avatar_url"},
                "author": {"name": "name",
                           "username": "user",
                           "id": 2,
                           "state": "active",
                           "avatar_url": "avatar_url"}}]

comment_mr_json = [{"id": 11,
                    "body": "message body",
                    "attachment": None,
                    "author": {"name": "user",
                               "username": "user",
                               "id": 8,
                               "state": "active",
                               "avatar_url": "avatar_url"},
                    "created_at": "2014-10-25T14:43:54.863Z"}]

comment_issue_json = [{"id": 447,
                       "body": "message body",
                       "attachment": None,
                       "author": {"name": "user",
                                  "username": "user",
                                  "state": "active",
                                  "id": 8,
                                  "avatar_url": "avatar_url"},
                       "created_at": "2015-03-16T17:34:07.715Z"}]
