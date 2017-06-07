from faker import Faker, Factory
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
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
        """ Positive test on create user """
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
        """ Test that we can get user list """
        user_list = users.get()
        assert_is_instance(user_list, list,
                           "Data should be a list but got %s" % user_list)

    def test_filter_by_name(self):
        """ Test filtering user by name field """
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

    def test_filter_by_email(self):
        """ Test filtering user by email field """
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
                                           "data sent + id, sent %s but got %s" % (user, last_user))

    def test_filter_by_phone(self):
        """ Test filtering user by phone field """
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
                                           "data sent + id, sent %s but got %s" % (user, last_user))

    def test_filer_by_zipcode(self):
        """ Test filtering user by zipcode (inner field) """
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
                                           "data sent + id, sent %s but got %s" % (user, last_user))

    def test_filter_by_name_and_email(self):
        """ Test filtering user by two fields -last_user name and email """
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
                                           "data sent + id, sent %s but got %s" % (user, last_user))

    def test_full_text_search(self):
        """ Test full text search """
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

                # test that no wrong users returned
                def flatten(x):
                    return ''.join(flatten(i) if isinstance(i, dict) else unicode(i) for i in x.values())
                for user2 in user_list:
                    user2_text = flatten(user2)
                    assert_true(search_token.lower() in user2_text.lower(),
                                "User retrieved which does not contain search text (%s): %s"
                                % (search_token, user2))

                last_user = max(user_list, key=lambda user: user['id'])
                user.update(id=last_user['id'])
                assert_dict_equal(user, last_user, "Data of the last record should be equal to "
                                           "data sent + id, sent %s but got %s" % (user, last_user))
            yield test

    def test_filter_by_name_unicode(self):
        """ Test filter user by unicode name """
        user = self.__get_full_user_localized()
        users.post(user)
        search_name = user['name']
        user_list = users.get(name=search_name)
        assert_true(len(user_list) >=1, "At least one user should be found, but got %s" % user_list)
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record should be equal to the data sent + id, "
                                           "sent %s but got %s" % (user, last_user))

    def test_full_text_search_unicode(self):
        """ Test full text search by unicode text """
        user = self.__get_full_user_localized()
        users.post(user)
        search_token = user['name'][:2]
        user_list = users.get(q=search_token)
        assert_true(len(user_list) >= 1, "At least one user should be found, got %s" % user_list)
        last_user = max(user_list, key=lambda user: user['id'])
        user.update(id=last_user['id'])
        assert_dict_equal(user, last_user, "Data of the last record shoud be equal to the data sent + id, "
                                           "sent %s but got %s" % (user, last_user))

    def test_replace_user(self):
        """ Test replace user data by method PUT """
        user = self.__get_full_user_en()
        users.post(user)
        user_list = users.get()
        old_user = max(user_list, key=lambda user: user['id'])
        user_id = old_user['id']
        new_user = self.__get_minimal_user()
        users.put(user_id, new_user)
        user_list = users.get()
        last_user = max(user_list, key=lambda user: user['id'])
        new_user.update(id=user_id)
        assert_dict_equal(new_user, last_user)

    def test_update_user(self):
        """ Test update user data by method PATCH
        note: for inner fields whole dict should be replaced (current behavior) """
        user = self.__get_full_user_en()
        users.post(user)
        user_list = users.get()
        old_user = max(user_list, key=lambda user:user['id'])
        user_id = old_user['id']
        for new_json in ({'name': self.fake.name()},
                         {'address': {'street': self.fake.street_name()}}):
            def test():
                users.patch(user_id, new_json)
                user_list = users.get()
                last_user = max(user_list, key=lambda user: user['id'])
                old_user.update(new_json)
                assert_dict_equal(old_user, last_user)
            yield test

    def test_delete_user(self):
        """ Test delete user by method DELETE """
        user = self.__get_full_user_en()
        users.post(user)
        user_list = users.get()
        old_user = max(user_list, key=lambda user: user['id'])
        user_id = old_user['id']
        users.delete(user_id)
        new_user_list = users.get()
        assert_true(len(filter(lambda user: user['id'] == user_id, new_user_list)) == 0,
                    "Deleted user with id = %d should not be in the list" % user_id)
        assert_equals(len(user_list) - 1, len(new_user_list),
                      "New user list should be shorter by 1 than list before deletion, "
                      "was %d, now %d" % (len(user_list), len(new_user_list)))

    def test_create_user_with_id(self):
        """ Test create user with id specified in request """
        user = self.__get_full_user_en()
        user_list = users.get()
        user_id = max(user['id'] for user in user_list) + 1 if user_list else 1
        user.update(id=user_id)
        users.post(user)
        new_user_list = users.get()
        assert_equals(len(user_list) + 1, len(new_user_list),
                      "Users count should be increased by 1,"
                      " was %d, now %d" % (len(user_list), len(new_user_list)))
        assert_equals(user, new_user_list[-1],
                      "User should be created with the id passed, "
                      "sent %s, created %s" % (user, new_user_list[-1]))

    def test_sequence_after_create_user_with_id(self):
        """ Test that specifying id in request does not break id sequence for next users """
        user = self.__get_full_user_en()
        user_list = users.get()
        user_id = max(user['id'] for user in user_list) + 2 if user_list else 2
        user.update(id=user_id)
        users.post(user)
        for _ in xrange(2):
            user = self.__get_full_user_en()
            users.post(user)
            user_list = users.get()
            new_user = user_list[-1]
            assert_not_equal(user_id, new_user['id'],
                             "New user should be created with new id, created with %s" % user_id)
            user.update(id=new_user['id'])
            assert_dict_equal(user, new_user,
                              "New user should be created with the data sent, "
                              "sent %s, created %s" % (user, new_user))

    @attr(negative=True)
    def test_create_user_with_existing_id(self):
        """ Negative test on creation user with duplicate id """
        user = self.__get_full_user_en()
        user_list = users.get()
        last_user = max(user_list, key=lambda user: user['id'])
        user_id = last_user['id']
        user.update(id=user_id)
        users.post(user)
        new_user_list = users.get()
        assert_equals(len(user_list), len(new_user_list),
                      "Users count should remain the same, "
                      "was %d, now %d" % (len(user_list), len(new_user_list)))
        new_user = filter(lambda user: user['id'] == user_id, user_list)[0]
        assert_equals(last_user, new_user,
                      "User with existing id should remain unchanged, "
                      "was %s, now %s" % (last_user, new_user))

    @attr(negative=True)
    @SkipTest
    def test_create_user_with_wrong_data(self):
        """ Test create user with wrong data (list instead of dict)
        This fails, I think this is a bug because this behavior resulting 
        to broken json structure, filed https://github.com/typicode/json-server/issues/547
        """
        user_list = users.get()
        users.post([{'foo': 'bar'}])
        new_user_list = users.get()
        assert_equals(len(user_list), len(new_user_list),
                      "User count should remain the same, "
                      "was %d, now %d" % (len(user_list), len(new_user_list)))

    @attr(negative=True)
    def test_replace_user_with_wrong_id(self):
        """ Negative test on replace user by method PUT with non-existent id """
        user_list = users.get()
        user_id = max(user['id'] for user in user_list) + 1 if user_list else 1
        user = self.__get_minimal_user()
        users.put(user_id, user)
        new_user_list = users.get()
        assert_equals(len(user_list), len(new_user_list),
                      "Users count should remain unchanged, "
                      "was %d, now %d" % (len(user_list), len(new_user_list)))

    @attr(negative=True)
    def test_update_user_with_wrong_id(self):
        """ Negative test on update user by method PATCH with non-existent id """
        user_list = users.get()
        user_id = max(user['id'] for user in user_list) + 1 if user_list else 1
        json = {'name': self.fake.name()}
        users.patch(user_id, json)
        new_user_list = users.get()
        assert_equals(len(user_list), len(new_user_list),
                      "Users count should remain unchanged, "
                      "was %d, now %d" % (len(user_list), len(new_user_list)))

    @attr(negative=True)
    def test_delete_user_with_wrong_id(self):
        """ Negative test on delete user by method DELETE with non-existent id """
        user_list = users.get()
        user_id = max(user['id'] for user in user_list) + 1 if user_list else 1
        users.delete(user_id)
        new_user_list = users.get()
        assert_equals(len(user_list), len(new_user_list),
                      "Users count should remain unchanged, "
                      "was %d, now %d" % (len(user_list), len(new_user_list)))