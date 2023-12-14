from django.shortcuts import render
from rest_framework.views import APIView,Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.db.models.fields.related import ManyToManyField
from django.conf import settings
from urllib.parse import urljoin
from datetime import timedelta,datetime
from decimal import Decimal


# Create your views here.
from .models import Content,Thumbnail

from api import serializers

from .models import Genre,AudioLanguages,SubtitleLanguages,Location,Director,Producer,Cast,Actor,Actress,AgeRating,Category

# Create a dictionary to map content types to classes
content_type_mapping = {
    "genre": Genre,
    "audiolanguages": AudioLanguages,
    "subtitlelanguages": SubtitleLanguages,
    "location": Location,
    "director": Director,
    "producer": Producer,
    "cast": Cast,
    "actor": Actor,
    "actress": Actress,
    "agerating": AgeRating,
    "category":Category
}


class FillContent(APIView):

    permission_classes = [AllowAny]

    name_serializerclass = serializers.ContentSerializer

    def post(self,request,content_type):

        try:

            namserializer = self.name_serializerclass(data=request.data)
    
            content_type_class = content_type_mapping.get(content_type)


                # Check if a category with the same name already exists
            if namserializer.is_valid():
                    if content_type_class.objects.filter(name=namserializer.validated_data.get('name')).exists():
               
                        return Response({"error":  content_type+" with the same name is already present."}, status=400)

                    category=content_type_class.objects.create(
                        name=namserializer.validated_data.get('name')
                    )
                    category.save()

                    return Response({"success":"saved"})
            
            else:
                return Response({"error":namserializer.error_messages})
        except Exception as e:
            return Response({"error":str(e)}, status=400)


    

    def get(self,request,content_type):
        try:
            content_type_class = content_type_mapping.get(content_type)
            if content_type_class:
                object = content_type_class.objects.values('name').all()
                jsonObject = list(object)

                return Response({'success':True,'data':jsonObject})
        
            return Response({"error":"Some error occured"})
        
        except Exception as e:
            return Response({"error":str(e)})


class Contents(APIView):
    permission_classes = [AllowAny]

    add_contet_serializer = serializers.add_contents_serializer

    def post(self,request):
        add_content_data = self.add_contet_serializer(data=request.data)

        try:
            add_content_data.is_valid(raise_exception=True)
            data = add_content_data.validated_data
        except ValidationError as e:
            print("error",e.detail)

            
    
        try:
                # add_content_data.is_valid():
                

                genre_name = data.get('genre',[])
                title_name = data.get('title',"")
                description_name = data.get('description',[])
                age_rating_names = data.get('age_rating',[])
                release_name = data.get('release_date',"")
                # duration_name = timedelta(hours=data.get('duration').get('hours'),minutes=data.get('duration').get('minutes'))
                duration_name= data.get('duration')
                rating_name = data.get('rating'),
                location_name = data.get('location',[])
                director_name = data.get('director',[])
                producer_name = data.get('producer',[])
                cast_name = data.get('cast',[])
                actor_name = data.get('actor',[])
                actress_name = data.get('actress',[])
                is_trending_name = data.get('is_trending',"")

             
                
                content = Content.objects.create(
                    title=title_name,
                    description = description_name,
                    release_date = release_name,
                    is_trending = is_trending_name,
                    duration = duration_name,
                    rating = rating_name[0] if isinstance(rating_name,tuple) and len(rating_name)>0 else rating_name #dat.get('rating') is returing (Decimal('4.5'),) on rating_name
                )

            
              
                content.save()

                
                Listmodels = {
                    Genre:genre_name,
                    Location:location_name,
                    Director:director_name,
                    Producer:producer_name,
                    Cast:cast_name,
                    Actor:actor_name,
                    Actress:actress_name,
                    AgeRating: age_rating_names
                }

                for model,lists in Listmodels.items():
                    
                    #To check whether inputted content_type exists or not. If not add it
                    for name in lists:
                        if not model.objects.filter(name=name).exists():
                            
                            newInstance = model.objects.create(name=name)
                            newInstance.save()
                        modelInstance = model.objects.get(name=name)
                        
                        #suppose model = Genre
                        #model.__name__.lower() gives genre
                        content_field = model.__name__.lower()
                        
                        #This assumes that in your Content model, there's a field named content_field(genre) that represents a many-to-many relationship with the  model(Genre).
                        contentInstance = getattr(content,content_field)  #give Content.model

                     

                        contentInstance.add(modelInstance)    #Mapped the instance of Content and Model

                thumbnail = Thumbnail.objects.create(
                    saved_location = data.get('thumbnail'),
                    content = content
                )
                thumbnail.save()
                
             

                return Response({"success":True,"data":[{"title":title_name,
                        "genre":genre_name,
                        "description":description_name,
                        "age_rating":age_rating_names,
                        "release_date":release_name,
                        "duration":duration_name,
                        "rating":rating_name,
                        "loation":location_name,
                        "director":director_name,
                        "producer":producer_name,
                        "cast":cast_name,
                        "actor":actor_name,
                        "actress":actress_name,
                        "is_trending":is_trending_name,
                        "thumbnail":urljoin(settings.MEDIA_URL, str(thumbnail.saved_location))}]})

    

            
        except Exception as e:
               return Response({"error":str(e)})

    def get(self,request):

        filters ={}

        # Mapping between query parameters and model fields
        parameter_to_field={
            "genre":"genre__name",   # Many-to-many field to Genre model
            "title":"title",  # Normal field for the title
            "agerating":"agerating__name",
            "release_date":"release_date",
            "location":"location__name",
            "director":"director__name", # Assuming 'director' field is a ForeignKey to a Director model
            "producer":"producer__name",
            "cast":"cast__name",
            "actor":"actor__name",
            "actress":"actress__name",
            "is_trending":"is_trending"

        }
        
        try:
            for parameter,field in parameter_to_field.items():
                value = request.query_params.get(parameter)    #Gets parameter from the url 
                

                if value:
                    if '__' in field:
                        filters[field+"__in"] = value.split(',') #eg. genre__name__in checks the all element of the array
                    
                    else:
                        filters[field] = value

            content = Content.objects.all()


            if filters:
                content = content.filter(**filters)  #multiple filter


            # Retrieve all Content objects with related fields through prefetch_related
            
            movies=[]

            def Get_data(contents):
                movies =[
                {
                    "id":response.id,
                    "title":response.title,
                    "description":response.description,
                    "agerating":[agerating.name for agerating in response.agerating.all()],
                    "release_date":response.release_date.strftime('%Y-%m-%d') if response.release_date else None,
                    "duration":str(response.duration.seconds//3600)+"h"+" "+str((response.duration.seconds%3660)//60)+"m",
                    "rating":float(response.rating) if response.rating is not None else None,
                    "location":[location.name for location in response.location.all()],
                    "director":[director.name for director in response.director.all()],
                    "producer":[producer.name for producer in response.producer.all()],
                    "cast":[cast.name for cast in response.cast.all()],
                    "actor":[actor.name for actor in response.actor.all()],
                    "actress":[actress.name for actress in response.actress.all()],
                    "is_trending":response.is_trending,
                    "added_at":response.added_at,
                    
                }

                for response in contents
                ] 

                for thumbnail_info in movies:
                    thumbnail = Thumbnail.objects.get(content_id = thumbnail_info["id"])
                    thumbnail_info["thumbnail"]=thumbnail.saved_location.url
                    del thumbnail_info["id"]

                return movies
                
            # def Recent_Get(contents):
                movies =[
                {
                    "id":response.id,
                    "title":response.title,
                    "description":response.description,
                    "agerating":[agerating.name for agerating in response.agerating.all()],
                    "release_date":response.release_date.strftime('%Y-%m-%d') if response.release_date else None,
                    "duration":str(response.duration.seconds//3600)+"h"+" "+str((response.duration.seconds%3660)//60)+"m",
                    "rating":float(response.rating) if response.rating is not None else None,
                    "location":[location.name for location in response.location.all()],
                    "director":[director.name for director in response.director.all()],
                    "producer":[producer.name for producer in response.producer.all()],
                    "cast":[cast.name for cast in response.cast.all()],
                    "actor":[actor.name for actor in response.actor.all()],
                    "actress":[actress.name for actress in response.actress.all()],
                    "is_trending":response.is_trending,
                    "added_at":response.added_at,
                    
                }

                for response in contents
                ] 

                for thumbnail_info in movies:
                    thumbnail = Thumbnail.objects.get(content_id = thumbnail_info["id"])
                    thumbnail_info["thumbnail"]=thumbnail.saved_location.url
                    del thumbnail_info["id"]

                return movies
                
            six_month_ago= datetime.now()-timedelta(days=600)  #calculate the date 6 month before now

            contents_with_related =  content.prefetch_related('genre','agerating','location','director','producer','cast','actor','actress')

            recently_added = request.query_params.get('recent')
            latest_release = request.query_params.get('latest_release')
            trending = request.query_params.get('trending')

            if recently_added:
                movies=Get_data(contents_with_related.filter(added_at__gte=six_month_ago))
            if latest_release:
                movies = Get_data(contents_with_related.filter(release_at__gte=six_month_ago))
            if trending:
                movies = Get_data(contents_with_related.filter(is_trending=True))

            if not (recently_added and latest_release and trending):
                movies = Get_data(contents_with_related)
        

            return Response({"success":True,"data":movies})

        except Exception as e:
            return Response ({"error":str(e)})
    
    def delete (self,request):
        primary_key = request.query_params.get('pk')

        many_to_many_field = []

        try:
            if Content.objects.get(id=primary_key):
               
               content_instance = Content.objects.get(id=primary_key)
               image_instance = Thumbnail.objects.get(content_id=primary_key) #Content's id is saved as Thumbnail's content_id              

               #Checks whether the field in the Content Model have many to many relation with other Model or not.
               #If there is many to many relation append the field in the many_to_many_field list.
               for field in content_instance._meta.get_fields():
                   if(isinstance(field,ManyToManyField)):
                        many_to_many_field.append(field)


               data_to_be_sent =[{
                        "title":content_instance.title,
                        "genre":[genre.name for genre in content_instance.genre.all()],
                        "description":content_instance.description,
                        "age_rating":[agerating.name for agerating in content_instance.agerating.all()],
                        "release_date":content_instance.release_date.strftime('%Y-%m-%d') if content_instance.release_date else None,
                        "duration":str(content_instance.duration.seconds//3600)+"h"+" "+str((content_instance.duration.seconds%3660)//60)+"m",
                        "rating":float(content_instance.rating) if content_instance.rating is not None else None,
                        "loation":[location.name for location in content_instance.location.all()],
                        "director":[director.name for director in content_instance.director.all()],
                        "producer":[producer.name for producer in content_instance.producer.all()],
                        "cast":[cast.name for cast in content_instance.cast.all()],
                        "actor":[actor.name for actor in content_instance.actor.all()],
                        "actress":[actress.name for actress in content_instance.actress.all()],
                        "is_trending":content_instance.is_trending,
                        "thumbnail":urljoin(settings.MEDIA_URL, str(image_instance.saved_location))}]

            
               for field_name in many_to_many_field:
                      related_field = getattr(content_instance,field_name.name)
                      #This would remove the relationships between the Content and its fields before deleting the content instance.
                      related_field.clear()
                      

 
               image_instance.saved_location.delete(save=False) # Delete the associated image file

               content_instance.delete()   #delete the content
                

               return Response({"success":True,"data":data_to_be_sent})
            else:
                raise Exception ("Instnce not found")
            
        except Exception as e:
            return Response({"error":str(e)})
    
    def patch (self,request):

        update_content_data = self.add_contet_serializer(data=request.data,partial=True)
        primary_key = request.query_params.get('pk')

        try:
            update_content_data.is_valid(raise_exception=True)
            data = update_content_data.validated_data
        except ValidationError as e:
            return Response({"error":str(e)})
        

        try:
            content_instance = Content.objects.get(id=primary_key)

            content_instance.title = data.get('title',content_instance.title)
            content_instance.description = data.get('description',content_instance.description)
            content_instance.release_date = data.get('release_date',content_instance.release_date)
            content_instance.is_trending = data.get('is_trending', content_instance.is_trending)

            

            

            if data.get('thumbnail'):

                if Thumbnail.objects.filter(content_id=primary_key).exists():
                    image_instance = Thumbnail.objects.get(content_id=primary_key)

                    image_instance.saved_location.delete(save=False) # Delete the associated image file
                    image_instance.saved_location=data.get('thumbnail')
                    image_instance.save()

                else:
                    image_instance = Thumbnail.objects.create(
                        content = content_instance,
                        saved_location = data.get('thumbnail')
                    )
                    image_instance.save()
            else:
                image_instance = Thumbnail.objects.get(content_id=primary_key)
                image_instance.saved_location = image_instance.saved_location
                image_instance.save()

        

           
    

            content_instance.save()

        
            

            listModels={
                Genre:data.get('genre',content_instance.genre.all()),
                Location:data.get('location',content_instance.location.all()),
                Director:data.get('director',content_instance.director.all()),
                Producer:data.get('producer',content_instance.producer.all()),
                Cast:data.get('cast',content_instance.cast.all()),
                Actor:data.get('actor',content_instance.actor.all()),
                Actress:data.get('actress',content_instance.actress.all()),
                AgeRating:data.get('agerating',content_instance.agerating.all())
            }

            # print(content_instance.genre.all())
            
            for model,lists in listModels.items():         
                for name in lists:
                   
                    if not model.objects.filter(name=name).exists():
                        
                        newInstance = model.objects.create(name=name)
                        newInstance.save()
                        
                    modelInstance = model.objects.get(name=name)

                    content_field = model.__name__.lower()

                    content_instance_final = getattr(content_instance,content_field)

                    content_instance_final.add(modelInstance)

            
            data_to_be_sent =[{
                        "title":content_instance.title,
                        "genre":[genre.name for genre in content_instance.genre.all()],
                        "description":content_instance.description,
                        "age_rating":[agerating.name for agerating in content_instance.agerating.all()],
                        "release_date":content_instance.release_date.strftime('%Y-%m-%d') if content_instance.release_date else None,
                        "duration":str(content_instance.duration.seconds//3600)+"h"+" "+str((content_instance.duration.seconds%3660)//60)+"m",
                        "rating":float(content_instance.rating) if content_instance.rating is not None else None,
                        "loation":[location.name for location in content_instance.location.all()],
                        "director":[director.name for director in content_instance.director.all()],
                        "producer":[producer.name for producer in content_instance.producer.all()],
                        "cast":[cast.name for cast in content_instance.cast.all()],
                        "actor":[actor.name for actor in content_instance.actor.all()],
                        "actress":[actress.name for actress in content_instance.actress.all()],
                        "is_trending":content_instance.is_trending,
                        "thumbnail":urljoin(settings.MEDIA_URL, str(image_instance.saved_location))}]
            
            print(data_to_be_sent)

            return Response ({"success":True,"data":data_to_be_sent
                        
                        })


        except Exception as e:
            return Response ({"error":str(e)})





            


    


    










