from faker import Faker, Factory
from nose.tools import *

from clients import users


class TestUsers(object):
    fake = Faker()

    def __get_minimal_user(self):
        return {'name': self.fake.name()}

    def __get_full_user(self, fake):
        return {
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "address": {
                "street": fake.street_name(),
                "city": fake.city(),
                "zipcode": fake.zipcode() if hasattr(fake, 'zipcode') else None,
                "geo": {
                    "lat": str(fake.latitude()),
                    "lng": str(fake.longitude())
                }
            },
            "phone": fake.phone_number(),
            "website": fake.words(1)[0] + ".org",
            "company": {
                "name": fake.company(),
                "catchPhrase": fake.catch_phrase() if hasattr(fake, 'catch_phrase') else None,
                "bs": fake.bs() if hasattr(fake, 'bs') else None
            }
        }

    def __get_full_user_en(self):
        return self.__get_full_user(self.fake)

    def __get_full_user_localized(self):
        return self.__get_full_user(Factory.create('zh_CN'))

    def test_create_user(self):
        for case, json in (('User with minimal data', self.__get_minimal_user()),
                           ('User with all data', self.__get_full_user_en()),
                           ('User with data in not-ASCII locale', self.__get_full_user_localized())):
            def test():
                prev = users.get()
                users.post(json)
                now = users.get()
                assert_equals(len(prev) + 1, len(now),
                              case + ": Users count should increase by 1, "
                              "was %d but now %s" % (len(prev), len(now)))
                user_id = now[-1].get('id')
                assert_is_not_none(user_id, case + ": Created record should have id")
                json.update(id=user_id)
                assert_dict_equal(json, now[-1],
                                  case + ": Data of the last record should be equal to the data sent + id, "
                                  "sent %s but got %s" % (json, now[-1]))
            yield test

    def test_list_users(self):
        user_list = users.get()
        assert_is_instance(user_list, list,
                           "Data should be a list but got %s" % user_list)

    def test_filter_users_by_full_name(self):
        user = self.__get_full_user_en()
        users.post(user)
        search_name = user['name']
        user_list = users.get(name=search_name)
        assert_true(len(user_list) >= 1, "At least one record should be returned, "
                                                "but got %s" % user_list)
        for user2 in user_list:
            assert_true(search_name in user2['name'], "Got user that does not match search "
                                                      "name (%s): %s" % (search_name, user2))
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + id, sent %s but got %s" % (user, last_user))

    def test_filter_users_by_email(self):
        user = self.__get_full_user_en()
        users.post(user)
        search_email = user['email']
        user_list = users.get(email=search_email)
        assert_true(len(user_list) >= 1, "At least one user should be returned, but got %s"
                    % user_list)
        for user2 in user_list:
            assert_true(search_email in user2['email'], "Got user that does not match search "
                                                        "email (%s): %s" % (search_email, user2))
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + is, sent %s but got %s" % (user, last_user))

    def test_filter_user_by_email(self):
        user = self.__get_full_user_en()
        users.post(user)
        search_phone = user['phone']
        user_list = users.get(phone=search_phone)
        assert_true(len(user_list) >= 1, "At least one user should be returned, but got %s"
                    % user_list)
        for user2 in user_list:
            assert_true(search_phone in user2['phone'], "Got user that does not match search phone "
                                                        "(%s): %s" % (search_phone, user2))
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + is, sent %s but got %s" % (user, last_user))

    def test_filer_user_by_zipcode(self):
        user = self.__get_full_user_en()
        users.post(user)
        search_zipcode = user['address']['zipcode']
        user_list = users.get(**{'address.zipcode': search_zipcode})
        assert_true(len(user_list) >= 1, "At least one user should be returned, but got %s"
                    % user_list)
        for user2 in user_list:
            assert_true(search_zipcode in user2['address']['zipcode'], "Got user that does not "
                                                                       "match search zipcode (%s): %s"
                        % (search_zipcode, user2))
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + is, sent %s but got %s" % (user, last_user))

    def test_filter_by_name_and_email(self):
        user = self.__get_full_user_en()
        users.post(user)
        search_name = user['name']
        search_email = user['email']
        user_list = users.get(name=search_name, email=search_email)
        assert_true(len(user_list) >= 1, "At least one user should be returned, but got %s" % user_list)
        for user2 in user_list:
            assert_true(search_email in user2['email'] and search_name in user2['name'],
                        "Got user that does not match search email (%s) and name (%s): %s"
                        % (search_email, search_name, user2))
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + is, sent %s but got %s" % (user, last_user))

    def test_full_text_search(self):
        user = self.__get_full_user_en()
        users.post(user)
        for search_token in (user['name'].split()[0],
                             user['name'].split()[1],
                             user['email'].split('@')[0],
                             user['company']['name'],
                             user['address']['street'][:3]):
            def test():
                user_list = users.get(q=search_token)
                assert_true(len(user_list) >= 1, "At least one user should be returned by token '%s', "
                                                 "but got %s" % (search_token, user_list))
                last_user = max(user_list, key=lambda user: user['id'])
                user.update(id=last_user['id'])
                assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + is, sent %s but got %s" % (user, last_user))
            yield test
