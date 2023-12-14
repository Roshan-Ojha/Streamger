from django.db import models

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
 
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AudioLanguages(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class SubtitleLanguages(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Location(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Director (models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Producer (models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    
class Cast (models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Actor (models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Actress (models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class AgeRating(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name
    

 
class Content (models.Model):
    genre = models.ManyToManyField(Genre)  # Each genr can belong to multiple Content, and each Content can have multiple Genre associated with it.
    title = models.CharField(max_length=255)
    description = models.TextField() 
    agerating=models.ManyToManyField(AgeRating) 
    release_date = models.DateField()
    duration = models.DurationField()
    rating = models.DecimalField(max_digits=2,decimal_places=1,null=True,blank=True)
    location=models.ManyToManyField(Location)
    director=models.ManyToManyField(Director)
    producer=models.ManyToManyField(Producer)
    cast=models.ManyToManyField(Cast)
    actor=models.ManyToManyField(Actor)
    actress=models.ManyToManyField(Actress)
    is_trending=models.BooleanField(null=True,blank=True)
    added_at = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.title
    

# class Thumbnail(models.Model):
#     # In this case, the Thumbnail model has a ForeignKey relationship with the Content model. When an Content instance is deleted,
#     #  on_delete=models.CASCADE ensures that all related Thumbnail instances associated with that Content will also be deleted.
#     content=models.ForeignKey(Content,on_delete=models.CASCADE)  

#     saved_location = models.ImageField(upload_to='thumbnails/')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.content.title

class Thumbnail(models.Model):

    # In this case, the Thumbnail model has a ForeignKey relationship with the Content model. When an Content instance is deleted,
   #  on_delete=models.CASCADE ensures that all related Thumbnail instances associated with that Content will also be deleted.
   #This automatically adds content_id field to the Thumbnail model which have the id of the Content model
    content = models.ForeignKey(Content,on_delete=models.CASCADE)

    saved_location = models.ImageField(upload_to="thumbnails/") #Saves images inside thumbnails folder inside media folder
                                                                #Image should be passed to this field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.content.title




    
