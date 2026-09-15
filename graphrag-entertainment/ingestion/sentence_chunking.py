from ingestion.models import Document, Chunk
from ingestion.sentence_splitter import split_sentences


def chunk_document(document:Document,document_id:int) ->list[Chunk]:


    sentence_list: list[str]=split_sentences(document.content)
    sentence_groups = group_sentences(sentences_list)


    return [
        Chunk(
            document_id=document_id,
            chunk_index=i,
            content=sent,

        ) for i,sent in enumerate(sentence_groups)
    ]



    
def create_chunks(document:Document)
