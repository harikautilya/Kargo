from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR


class BaseJsonView:
    """
    Standard json response view, holds helper method for ease of use
    """

    def __init__(self):
        pass

    def generic_response(self, obj: dict, err: dict):
        """
        Generic response for application
        """
        return {"result": obj, "err": err}

    def ok_response(self, obj: dict):
        """
        success response with 200
        """
        return Response(self.generic_response(obj=obj, err={}), status=HTTP_200_OK)

    def err_reponse(self, err):
        """
        Error response with 500 
        """
        return Response(self.generic_response(obj={}, err=err), status=HTTP_500_INTERNAL_SERVER_ERROR)