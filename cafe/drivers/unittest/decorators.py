"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
TAGS_DECORATOR_TAG_LIST_NAME = "__test_tags__"
TAGS_DECORATOR_ATTR_DICT_NAME = "__test_attrs__"


def tags(*tags, **attrs):
    def wrap(func):
        setattr(func, TAGS_DECORATOR_TAG_LIST_NAME, [])
        setattr(func, TAGS_DECORATOR_ATTR_DICT_NAME, {})
        func.__test_tags__.extend(tags)
        func.__test_attrs__.update(attrs)
        return func
    return wrap
