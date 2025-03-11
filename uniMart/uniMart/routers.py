import sys
import random
class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        if 'test' in sys.argv:
            return 'default'
        # Read from replica by default
        return 'default'#random.choice(['replica', 'replica-2'])

    def db_for_write(self, model, **hints):
        # Write to primary
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations if both objects are in the same database
        db_obj1 = self.db_for_read(obj1.__class__, **hints)
        db_obj2 = self.db_for_read(obj2.__class__, **hints)
        if db_obj1 and db_obj2:
            return db_obj1 == db_obj2
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Make sure the auth and contenttypes apps only appear in the 'primary' db
        if app_label in ('auth', 'contenttypes'):
            return db == 'default'
        return True