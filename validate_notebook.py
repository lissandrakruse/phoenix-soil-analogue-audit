"""Sequential Python execution of notebook cells, not a Jupyter-kernel validation."""
from pathlib import Path
import os,json,io,contextlib,base64
from IPython import display as ipd
R=Path(__file__).resolve().parent;os.chdir(R)
p=R/'Texas_Phoenix_Numerical_Study.ipynb';n=json.loads(p.read_text());env={'__name__':'__main__'};count=0
for cell in n['cells']:
 if cell['cell_type']!='code':continue
 count+=1;out=[];buf=io.StringIO()
 def show(*objects,**kw):
  for obj in objects:
   data={'text/plain':str(obj)}
   if hasattr(obj,'_repr_html_'):
    h=obj._repr_html_()
    if h is not None:data['text/html']=h
   if isinstance(obj,ipd.Image) and obj.filename:
    data['image/png']=base64.b64encode(Path(obj.filename).read_bytes()).decode()
   out.append({'output_type':'display_data','metadata':{},'data':data})
 ipd.display=show
 with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):exec(compile(''.join(cell['source']),f'cell{count}','exec'),env)
 if buf.getvalue():out.append({'output_type':'stream','name':'stdout','text':buf.getvalue()})
 cell['execution_count']=count;cell['outputs']=out;print('PASS cell',count,flush=True)
n['metadata']['execution_validation']={'mode':'sequential Python exec; not Jupyter kernel','code_cells_passed':count}
p.write_text(json.dumps(n,indent=1));print('PASS all notebook code cells',count)
