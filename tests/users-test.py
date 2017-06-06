from faker import Faker
from nose.tools import *

from clients import users


class TestUsers(object):
    fake = Faker()

    def __get_minimal_user(self):
        return {'name': self.fake.name()}

    def __get_full_user(self):
        return {
            "name": self.fake.name(),
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "address": {
                "street": self.fake.street_name(),
                "city": self.fake.city(),
                "zipcode": self.fake.zipcode(),
                "geo": {
                    "lat": str(self.fake.latitude()),
                    "lng": str(self.fake.longitude())
                }
            },
            "phone": self.fake.phone_number(),
            "website": self.fake.words(1)[0] + ".org",
            "company": {
                "name": self.fake.company(),
                "catchPhrase": self.fake.catch_phrase(),
                "bs": self.fake.bs()
            }
        }

    def test_create_user(self):
        prev = users.get()
        json = self.__get_minimal_user()
        users.post(json)
        now = users.get()
        assert_equals(len(prev) + 1, len(now),
                      'Users count should increase by 1, '
                      'was %d but now %s' % (len(prev), len(now)))
        user_id = now[-1].get('id')
        assert_is_not_none(user_id, "Created record should have id")
        json.update(id=user_id)
        assert_dict_equal(json, now[-1],
                          'Data of the last record should be equal to the data sent + id, '
                          'sent %s but got %s' % (json, now[-1]))

    def test_list_users(self):
        user_list = users.get()
        assert_is_instance(user_list, list,
                           "Data should be a list but got %s" % user_list)

    def test_filter_users_by_full_name(self):
        user = self.__get_full_user()
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
        user = self.__get_full_user()
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
        user = self.__get_full_user()
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
        user = self.__get_full_user()
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
        user = self.__get_full_user()
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
        user = self.__get_full_user()
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
