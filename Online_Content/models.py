from django.db import models
from django.urls import reverse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk, urllib, request, string, re
from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from django.http import HttpResponse
import io
from matplotlib import pyplot
analyser = SentimentIntensityAnalyzer()
# Create your models here.
class Topic(models.Model):
    
    name = models.CharField(max_length=200, help_text='Enter a type of article topic')
    
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('topic-detail', args=[str(self.id)])
class Source(models.Model):
    
    name = models.CharField(max_length=200, help_text='Enter a source which articles are published')
    
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('source-detail', args=[str(self.id)])
class Author(models.Model):
    full_name = models.CharField(max_length=100)
    

    class Meta:
        ordering = ['full_name']
    
    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.full_name}'
class Article(models.Model):
    topic = models.ForeignKey(Topic,on_delete=models.SET_NULL, null=True,help_text='Select a topic for this article')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=1000, null= True)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    date_of_publish = models.DateField(null=False)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True,help_text='Select a source for this article')
    url = models.URLField(max_length=1000, help_text='Enter a url that links to the article.')
    class Meta:
        ordering = ['-date_of_publish']
    
    def __str__(self):
        """String for representing the Model object."""
        return self.title
    
    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('article-detail', args=[str(self.id)])
    def display_topic(self):
       
        return ', '.join(topic.name for topic in self.topic.all())
    def display_source(self):
        
        return ', '.join(source.name for source in self.source.all())
    
    display_topic.short_description = 'Topic'
    display_source.short_description = 'Source'
class Article_content(models.Model):
    id=models.ForeignKey('Article', primary_key=True,on_delete=models.CASCADE,unique = True )
    content = models.TextField(help_text='Enter the full content for the article.')
    def get_getattitude(self):
        score=analyser.polarity_scores(self.content)['compound']
        if score > 0.5:
            result = 'Positive'
        elif score < -0.5:
            result = 'Negative'
        else:
            result = 'Neutral'
        return(result)
    attitude = property(get_getattitude)
    def key_word(self):
        rawdata = BeautifulSoup(self.content, 'html.parser').get_text() 
        rawdata=rawdata.lower() 
        rawdata=re.sub(r'\d+', '', rawdata) 
        tokens = word_tokenize(rawdata) 
        list0 = stopwords.words('English')
        list1 = ['airpods—the','case—are']
        sw = list0
        sw.extend(list1)
        new_token=list()
        for t in tokens:
            if t not in sw:
               new_token.append(t)
        punc=list(string.punctuation) # list puntuations from string package
        punc.append('“')  # add other signs that do not contained in sting list
        punc.append('”')
        punc.append('’')
        punc.append('\'') 
        punc.append("n't")
        punc.append("'m")
        punc.append("th")
        punc.append("'d")
        punc.append("'ve")
        punc.append("'re")
        punc.append("'ll")
        punc.append("--")
        punc.append("-a")
        punc.append("'s")
        punc.append("\"")
        punc.append("re")
        punc.append("will")
        punc.append("airpod")
        punc.append("airpods")
        punc.append("apple")
        punc.append("people")
        punc.append("products")
        punc.append("product")
        punc.append("years")
        punc.append("companies")
        punc.append("company")
        new_token2=list()
        for t in new_token:
             if t not in punc:
                 new_token2.append(t) # this list contain key words
        tagged = nltk.pos_tag(new_token2)
        l = list()
        for x in tagged:
            if x[1] =='NN' or x[1] =='NNS':
                l.append(x[0])
        return l
    def competiter_fig(self):
        target=self.content
        Competitor =('samsung','galaxy','sony','huawei','powerbeats','google','pixel','jbl','powerhbq')
        Competitor=list(Competitor)
        def countW(s,n,W):
           raw = BeautifulSoup(s, 'html.parser').get_text()
           raw=raw.lower()
           raw=re.sub(r'\d+', '', raw)
           tokens = word_tokenize(raw)
           sw = stopwords.words('English')
           new_token=list()
           for t in tokens:
               if t not in sw:
                   new_token.append(t)
           punc=list(string.punctuation)
           manualcheck= ['“','”','’',"n't","'m","th","'d","'s","eant",'priyanka',
                  'bangalore','std','hi','zoe','``',"''",'—',"'re","'ll","'ve",'eh','\x80','airpods','airpod','apple','also'
                 ,'said','want','like','make','even','get','siri','products','product']
           punc.extend(manualcheck)
           new_token2=list()
           for t in new_token:
               if t not in punc:
                  new_token2.append(t)
           freq= nltk.FreqDist(new_token2)
           tryo = pd.DataFrame(list(dict(freq).items()))
           tryo=tryo.sort_values(by=1, ascending=False)
           tryo.columns = ['Words', 'freq']
           if W in list(tryo.Words):
               result= int(tryo[tryo.Words==W].freq)
               return(result)
           else:
               return(0) 
        MT=list()
        for comp in Competitor:
            t2=countW(target,len(target),comp)
            MT.append(t2)
        if any(MT):
            result=pd.DataFrame({'comp': Competitor,'MT': MT})
            fig,ax=plt.subplots()
            ax=result.plot.bar(x='comp', y='MT', rot=0)
            buf = io.BytesIO()
            canvas = FigureCanvasAgg(fig)
            canvas.print_png(buf)
            response=HttpResponse(buf.getvalue(),content_type='image/png')
            # if required clear the figure for reuse 
            fig.clear()
            # I recommend to add Content-Length for Django
            response['Content-Length'] = str(len(response.content))
            return response
        else:
            
            return False
        
    def __int__(self):
        """String for representing the Model object."""
        return self.id