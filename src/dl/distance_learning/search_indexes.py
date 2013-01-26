from haystack import indexes
from distance_learning.models import Video

class VideoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', boost=2)
    video_type = indexes.CharField(model_attr='video_type')
    video_subject = indexes.CharField(model_attr='subject')
    content_auto = indexes.EdgeNgramField(
            use_template=True,
            template_name='search/indexes/distance_learning/video_text.txt')

    def get_model(self):
        return Video

    def index_queryset(self):
        return Video.objects.all_approved()
