=======
Models
=======

One of the challenges in testing non-UI based applications is handling communication protocols between the test harness and
the application under test. Abstracting this layer between the application and harness not only removes the concern of how
communication occurs from the perspective of the test developer, but also makes it easier for the harness to adapt to changes in the
structure of communication.

As part of the OpenCafe design strategy, we wanted to define a standard way of handling data serialization
that was also generic enough to be used with any protocol. Doing so enabled us make other design decisions, such as
making the serialization process transparent to the test developer (this is explained in
detail in the clients section).

Design
------

Models in OpenCafe are very similar data transfer objects (DTOs). However, OpenCafe models differ from DTOs as they do
define some functions. However, the purpose of any functions defined by a model should be limited to
converting the model to and from another format. For example, a model that will be used in requests to a REST API would
have functions to convert the object to JSON and XML, while an object that represents REST responses would
contain functions to convert JSON or XML back to an object. By convention, these functions are named _obj_to_<format>
and _<format>_to_obj. This convention is used by other elements in the framework to determine at execution time
which type of serialization should be used.

For convenience, you may want to implement the __eq__ and __ne__ functions to allow standard comparison functions such as
"in" and "not in" to be used in relation to the model. If you do this, make sure to implement both functions. Implementing
__eq__ without implementing __ne__ will cause comparisons to not work as expected.

Example - Models for a REST API
-------------------------------

In the example where the application under test is a REST API, the protocols the application is likely to understand
would be JSON and possibly XML. Our tests will need to be able to send and receive requests in both formats to be
able to handle all possible scenarios.

For the purpose of this example, we'll focus on a common need: authentication. Per our specification, our system is
expecting a request in the following format::

    JSON: { "auth": { "username" <user>, "api_key": <key>, "tenant_id": <tenant_id> }}
    XML: <auth api_key="user" tenant_id="user" username="user" />


Representing this request as an object is straightforward as it only has three fields: username, api_key, and tenant_id::

    class AuthRequest(AutoMarshallingModel):

        def __init__(self, username, api_key, tenant_id):
            self.username = username
            self.api_key = api_key
            self.tenant_id = tenant_id

Rather than inheriting from just object, I'm choosing to inherit to inherit from one of the OpenCafe base classes,
AutoMarshallingModel. This class exposes the "serialize" and "deserialize" functions, which will be used to
transform the object when needed. However, for that to work correctly, this model needs to implement functions to
perform the necessary types of serialization, JSON and XML::

    import json
    import xml.etree.ElementTree as ET

    def _obj_to_json(self):
        body = {
            'username': self.username,
            'api_key': self.api_key,
            'tenant_id': tenant_id
        }
        return json.dumps({"auth": body})

    def _obj_to_xml(self):
        element = ET.Element('auth')
        element.set('username', self.username)
        element.set('api_key', self.api_key)
        element.set('tenant', self.tenant_id)
        return ET.tostring(element)


