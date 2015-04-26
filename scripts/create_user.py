__author__ = 'Paul'

from util import model


def main():
    conn = model.DBConnection('development')
    user_collection = model.UserCollection(conn)
    user = model.User(
        user_collection,
        email='admin',
        password='admin',
        first_name='admin',
        last_name='admin')
    user.save()

    admin = user_collection.get_item(
        email='admin')
    print admin

if __name__ == '__main__':
    main()