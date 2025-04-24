class Responses:
    @staticmethod
    def success(code=None, data=None, description=None):
        return {
            'code': code,
            'data': data,
            'description': description,
        }
    
    @staticmethod
    def jwt(code=None, data=None, accessToken=None, description=None):
        return {
            'code': code,
            'data': data,
            'accessToken': accessToken,
            'description': description,
        }

    @staticmethod
    def error(code = None, description = None, ):
        return {
            'code': code,
            'description': description,
            } 
            