from proxy.transformers import ResponseTransformer, RequestTransformer


class TestResponseTransformer(ResponseTransformer):
    """
    A test transformer that replaces every instance of the word "Name" with "Foo".
    """
    def transform_response(self, response):
        response.content = response.content.replace(self.params.get('test_parameter'), "Foo")
        return response


class TestRequestTransformer(RequestTransformer):

    def transform_request(self, request):
        request.GET['foo'] = 'bar'
        return request

