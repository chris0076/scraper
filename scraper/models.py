from django.db import models

class Type(models.Model):
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name

class Course(models.Model):
    number = models.CharField(max_length=10)
    subject = models.CharField(max_length=10)
    prereqs = models.CharField(max_length=255)
    coreq = models.OneToOneField("self", null=True)
    types = models.ManyToManyField(Type)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    credits = models.CharField(max_length=30)
    # levels = models.ForeignKey("Level")

    def __unicode__(self):
        return self.title

class Class(models.Model):
    course = models.ForeignKey("Course", null=True)
    campus = models.CharField(max_length=100)
    crn = models.CharField(max_length=10)
    seats = models.IntegerField(null=True)
    enrolled = models.IntegerField(null=True)
    instructor = models.CharField(max_length=100)
    section = models.CharField(max_length=10)

    def __unicode__(self):
        return "%s %s" % (self.crn, self.course)

    @property
    def locations(self):
        return Location.objects.filter(c=self)

class Location(models.Model):
    c = models.ForeignKey("Class")
    online = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    days_of_week = models.CharField(max_length=10, null=True)
    building = models.CharField(max_length=100, null=True)
    room = models.CharField(max_length=20, null=True)

    def __unicode__(self):
        if self.online:
            string = "Online"
        else:
            string = "%s %s %s-%s on %s" % (self.building, self.room, self.start_time, self.end_time, self.days_of_week)
        return string