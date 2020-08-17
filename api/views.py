from .models import *
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import jwt
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.urls import resolve
from .middleware import checkcounter,resetcounter
# Create your views here.

APP_SECRET = "CGDFXE&^TYIHGFRDT%&^T&^(&*^RIUKHVGCT^&7875426DE$^%"
MOVIE_API_ID = "iNd3jDMYRKsN1pjQPMRz2nrq7N99q4Tsp9EY9cM0"
MOVIE_API_SECRET= "Ne5DoTQt7p8qrgkPdtenTK8zd6MorcCR5vXZIJNfJwvfafZfcOs4reyasVYddTyXCz9hcL5FGGIVxw3q02ibnBLhblivqQTp4BIC93LZHj4OppuHQUzwugcYu7TIC5H1"
MOVIE_API_URL = "https://demo.credy.in/api/v1/maya/movies/"
NUMBER_OF_RETRY = 3
NO_RETRY_ERROR_CODES = [200,404] 


def get_view_base_url(request):
    protocol = 'https://' if request.is_secure() else 'http://'
    hostpart = request.get_host()
    view_endpoint = request.resolver_match.url_name
    return "{}{}/{}/".format(protocol,hostpart,view_endpoint)


def token_checker(func):
    def main_func(request,*args, **kwargs):
        try:
            token = request.headers['Access-token']
            try:
                dec_dict = jwt.decode(token, APP_SECRET, algorithms=['HS256'])
                if 'uuid' in dec_dict and 'username' in dec_dict:
                    return func(request,*args, **kwargs)
                else:
                    return JsonResponse({"is_success":False , "error":"Invalid access-token"}, status=403) 
            except Exception as e:
                return JsonResponse({"is_success":False , "error":"Invalid access-token"}, status=403)  
        except Exception as e:
            return JsonResponse({"is_success":False , "error":"Invalid access-token"}, status=403) 
    return main_func 


def request_to_movie(url):
    for i in range(NUMBER_OF_RETRY):
        res = requests.get(url, verify=False, auth=requests.auth.HTTPBasicAuth(MOVIE_API_ID, MOVIE_API_SECRET))
        if res.status_code in NO_RETRY_ERROR_CODES:
            break
    return res


@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            received_json_data=json.loads(request.body)
            username = received_json_data.get('username')
            password = received_json_data.get('password')
            encrypt_password = make_password(password)
            if not username or not password:
                raise Exception("Both username and password fields are required")
            if user.objects.filter(username=username).exists():
                raise Exception("Username already exist. Please use a different username")
            record = user(username=username,password=encrypt_password)
            record.save()
            if record.uuid:
                obj = {"username":username,"uuid":record.uuid}
                encoded_jwt = jwt.encode(obj, APP_SECRET, algorithm='HS256').decode("utf-8")
                resp = dict(access_token=encoded_jwt)
                return JsonResponse(resp)
            else:
                raise Exception("An unknown error occured.")
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"is_success":False, "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"is_success":False , "error":"Method not allowed"}, status=405)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            received_json_data=json.loads(request.body)
            username = received_json_data.get('username')
            password = received_json_data.get('password')
            if not username or not password:
                raise Exception("Both username and password fields are required")
            if not user.objects.filter(username=username).exists():
                raise Exception("Username and passord combination is wrong.")
            record = user.objects.get(username=username)
            is_validate = check_password(password,record.password)
            if is_validate:
                obj = {"username":username,"uuid":record.uuid}
                encoded_jwt = jwt.encode(obj, APP_SECRET, algorithm='HS256').decode("utf-8")
                resp = dict(access_token=encoded_jwt)
                return JsonResponse(resp)
            else:
                raise Exception("An unknown error occured.")
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"is_success":False, "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"is_success":False , "error":"Method not allowed"}, status=405)


@csrf_exempt
@token_checker
def movies(request):
    if request.method == "GET":
        try:
            page = request.GET.get('page', None)
            url = "{}?page={}".format(MOVIE_API_URL,page) if page else MOVIE_API_URL
            res = request_to_movie(url)
            resp_json = json.loads(res.text)
            if 'error' in resp_json:
                return JsonResponse(resp_json, safe=False)   
            try:
                output = {}
                output["next"] = resp_json["next"].replace(MOVIE_API_URL,get_view_base_url(request)) if resp_json["next"] else None
                output["previous"] = resp_json["previous"].replace(MOVIE_API_URL,get_view_base_url(request)) if resp_json["previous"] else None
                output["data"] = resp_json.get("results" ,[])
                return JsonResponse(output)
            except Exception as e:
                print(e)
                return JsonResponse({"is_success":False, "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"is_success":False, "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"is_success":False , "error":"Method not allowed"}, status=405)


@csrf_exempt
@token_checker
def all_collection(request):
    if request.method=='GET':
        try:
            output= {"is_success":True , 
                    "data":{
                        "collections":[],
                        "favourite_genres" : []
                        }
                    }
            token = request.headers['Access-token']
            dec_dict = jwt.decode(token, APP_SECRET, algorithms=['HS256'])
            user_id=user.objects.get(uuid=dec_dict['uuid'])
            all_collections = collection.objects.filter(user_id=user_id)
            output["data"]["collections"] = list(all_collections.values('uuid','title','description'))
            genres_arr = []
            for each_movies in list(movie.objects.filter(collection_id__in=all_collections).values('genres')):
                if each_movies['genres'] != '' : genres_arr.extend(each_movies['genres'].split(',')) # Splited as there could be multiple genres comma separeted
            genres_counter = {}
            for genres in genres_arr:
                if genres in genres_counter: genres_counter[genres] += 1
                else: genres_counter[genres] = 1
            popular_genres = sorted(genres_counter, key = genres_counter.get, reverse = True)
            output["data"]["favourite_genres"] = popular_genres[:3]
            return JsonResponse(output)
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"is_success":False , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    elif request.method=='POST':
        try:
            token = request.headers['Access-token']
            dec_dict = jwt.decode(token, APP_SECRET, algorithms=['HS256'])
            user_id=user.objects.get(uuid=dec_dict['uuid'])
            received_json_data=json.loads(request.body)
            title = received_json_data.get('title')
            description = received_json_data.get('description')
            if not title or not description:
                raise Exception("The Title, Description of collection are mandatory.")
            new_collections = collection(title=title,description=description, user_id=user_id)
            new_collections.save()
            movies = received_json_data.get('movies')
            if not new_collections.uuid:
                raise Exception("An unknown error occured.")
            collection_uuid = new_collections.uuid
            for each_movie in movies:
                title=each_movie.get('title')
                description=each_movie.get('description')
                genres=each_movie.get('genres', "")
                uuid=each_movie.get('uuid')
                if not title or not description or not uuid:
                    delete_collection = collection.objects.get(uuid=collection_uuid)
                    delete_collection.delete()
                    raise Exception("The Title, Description and UUID of movies are mandatory.")
                else:
                    added_movie = movie(title=title,description=description,genres=genres,uuid=uuid, collection_id=new_collections) 
                    added_movie.save()
            return JsonResponse({"collection_uuid":collection_uuid}, status=200)
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"is_success":False , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"is_success":False , "error":"Methods not allowed"}, status=405)

@csrf_exempt
@token_checker
def selected_collection(request, collection_uuid):
    if request.method=='DELETE':
        try:
            if not collection_uuid : 
                raise Exception("collection_uuid is a mandatory parameter which is missing.")
            instance = collection.objects.get(uuid=collection_uuid)
            instance.delete()
            return JsonResponse({"is_success":True , "message":{"response":"Successfully deleted the collection with collection_uuid: {}".format(collection_uuid)}})
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"is_success":False , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    elif request.method=='GET':
        output={
                "title": "",
                "description": "",
                "movies": []
                }
        try:
            #selected_collection_record = list(collection.objects.filter(uuid=id)) 
            if not collection_uuid : 
                raise Exception("collection_uuid is a mandatory parameter which is missing.")
            collection_data = collection.objects.get(uuid=collection_uuid)
            output["title"] = collection_data.title
            output["description"] = collection_data.description
            for each_movies in list(movie.objects.filter(collection_id=collection_data).values()):
                # print(each_movies.description)
                output["movies"].append(each_movies)
            return JsonResponse(output)
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"status":"error" , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    elif request.method=='PUT':
        try:
            output = {}
            collection_object = collection.objects.get(uuid=collection_uuid)
            received_json_data=json.loads(request.body)
            title = received_json_data.get('title',None)
            description = received_json_data.get('description', None)
            movies = received_json_data.get('movies',None)
            if title : 
                collection_object.title = title
            if description : 
                collection_object.description = description
            collection_object.save()
            old_movies = movie.objects.filter(collection_id=collection_object)            
            output["title"] = collection_object.title
            output["description"] = collection_object.description
            output["movies"] = list(old_movies.values())
            if movies :
                old_movies.delete()
                output["movies"] = []
                for each_movie in movies:
                    title=each_movie.get('title')
                    description=each_movie.get('description')
                    genres=each_movie.get('genres', "")
                    uuid=each_movie.get('uuid')
                    if not title or not description or not uuid:
                        raise Exception("The Title, Description and UUID of all movies are mandatory.")
                    else:
                        added_movie = movie(title=title,description=description,genres=genres,uuid=uuid, collection_id=collection_object) 
                        added_movie.save()
                        output["movies"].append(each_movie)
            return JsonResponse(output)
            
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"status":"error" , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"status":"error" , "error":"Methods not allowed"}, status=405)


@csrf_exempt
@token_checker
def request_count(request):
    if request.method == "GET":
        try:
            output = {"requests": checkcounter()}
            return JsonResponse(output)
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"status":"error" , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"status":"error" , "error":"Methods not allowed"}, status=405)


@csrf_exempt
@token_checker
def reset_count(request):
    if request.method == "POST":
        try:
            if resetcounter() == 0:
                output = {"message": "request count reset successfully"}
            else:
                raise Exception("Unknon error occured")
            return JsonResponse(output)
        except Exception as e:
            print("EXCEPTION OCCURED : ",e)
            return JsonResponse({"status":"error" , "error":"Unable to process your request. Error detail : {}".format(str(e))}, status=500)
    else:
        return JsonResponse({"status":"error" , "error":"Methods not allowed"}, status=405)

