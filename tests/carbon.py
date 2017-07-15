import graphene

class Person(graphene.ObjectType):
    uuid = graphene.ID()
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()

    def resolve_full_name(self, args, context, info):
        return '{} {}'.format(self.first_name, self.last_name)
