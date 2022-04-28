1) Index input documents: 
  + For windows: python index.py input_dir output_dir\

2) Query to find relevant documents:
  + For windows:
    .Without weight: python query.py *query term(s)*. For instance, python query.py cat dog mouse
    .With weight: python query.py Wt *weight1* *term1* *weight2* *term2*... For instance, python query.py Wt 0.3 cat 0.4 dog 0.3 mouse
