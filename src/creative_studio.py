"""Creative Studio: image/PDF conversion, AI diagrams, prompt PDF/PPT, image-note tutor."""
from __future__ import annotations
import io, json, re, textwrap
from pathlib import Path
import streamlit as st
from PIL import Image, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image as RLImage, KeepTogether
from reportlab.lib.units import mm
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from src.ai import generate, generate_with_image

GOLD = "C5AE68"
DARK = "231F20"
CARD = "302C2D"
TEXT = "F5F2EA"


def _header():
    st.title("Creative Studio")
    st.caption("Turn study material and ideas into useful visual and downloadable learning resources.")
    st.markdown("<div class='robo-card'><h3>Creative Workshop</h3><p>Convert • Visualise • Explain • Create</p></div>", unsafe_allow_html=True)


def _ai(prompt):
    result = generate(prompt)
    if not result:
        return None
    if result.startswith((
        "GEMINI API KEY NOT FOUND",
        "GEMINI API KEY NOT CONFIGURED",
        "GEMINI AUTHENTICATION ERROR",
        "GEMINI API LIMIT",
        "GEMINI MODEL ERROR",
        "GEMINI API ERROR",
        "GEMINI IMAGE ERROR",
        "CONNECTION ERROR"
    )):
        st.error(result)
        return None
    return result


def _safe_filename(name, default="studigence_output"):
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()).strip("_")
    return (name[:60] or default)


def _pdf_bytes(title, body, image_bytes=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=19*mm, leftMargin=19*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="STTitle", parent=styles["Title"], textColor=colors.HexColor("#8E793E"), alignment=TA_CENTER, fontSize=21, leading=26, spaceAfter=14))
    styles.add(ParagraphStyle(name="STHeading", parent=styles["Heading2"], textColor=colors.HexColor("#8E793E"), fontSize=14, leading=18, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="STBody", parent=styles["BodyText"], fontSize=10, leading=15, spaceAfter=6))
    story = [Paragraph(title.replace("&", "&amp;"), styles["STTitle"]), Spacer(1, 5*mm)]
    if image_bytes:
        try:
            im = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            im.thumbnail((1400, 1800))
            temp = io.BytesIO(); im.save(temp, format="PNG"); temp.seek(0)
            story += [RLImage(temp, width=160*mm, height= min(220*mm, 160*mm*im.height/im.width)), Spacer(1, 5*mm)]
        except Exception:
            pass
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 3))
        elif line.startswith("#"):
            heading = line.lstrip("# ").replace("&", "&amp;")
            story.append(Paragraph(heading, styles["STHeading"]))
        elif re.match(r"^[-*•]\s+", line):
            story.append(Paragraph("• " + re.sub(r"^[-*•]\s+", "", line).replace("&", "&amp;"), styles["STBody"]))
        else:
            story.append(Paragraph(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), styles["STBody"]))
    doc.build(story)
    return buffer.getvalue()


def _parse_json(text):
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I)
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            try: return json.loads(match.group(0))
            except Exception: return None
    return None


def _diagram_png(title, nodes, edges):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    n = max(1, len(nodes))
    fig_h = max(4.2, min(10, 1.15*n + 1.5))
    fig, ax = plt.subplots(figsize=(11, fig_h))
    ax.set_xlim(0, 10); ax.set_ylim(0, n+1); ax.axis("off")
    ax.set_facecolor("#231F20"); fig.patch.set_facecolor("#231F20")
    positions = {}
    for i, node in enumerate(nodes):
        y = n - i - 0.2
        positions[str(node.get("id", i))] = (5, y)
        box = FancyBboxPatch((2.2, y-0.32), 5.6, 0.62, boxstyle="round,pad=0.12,rounding_size=0.12", facecolor="#302C2D", edgecolor="#C5AE68", linewidth=1.5)
        ax.add_patch(box)
        label = textwrap.fill(str(node.get("label", node.get("id", "Step"))), 55)
        ax.text(5, y, label, ha="center", va="center", color="#F5F2EA", fontsize=10)
    for edge in edges:
        a, b = str(edge.get("from")), str(edge.get("to"))
        if a in positions and b in positions:
            x1,y1=positions[a]; x2,y2=positions[b]
            arrow = FancyArrowPatch((x1,y1-0.36),(x2,y2+0.36),arrowstyle="-|>",mutation_scale=14,color="#C5AE68",linewidth=1.4)
            ax.add_patch(arrow)
    ax.text(5, n+0.55, title, ha="center", va="center", color="#E4CA80", fontsize=16, fontweight="bold")
    fig.tight_layout()
    out=io.BytesIO(); fig.savefig(out,format="png",dpi=180,bbox_inches="tight",facecolor=fig.get_facecolor()); plt.close(fig); out.seek(0)
    return out.getvalue()


def _mermaid(nodes, edges):
    lines=["flowchart TD"]
    for i,node in enumerate(nodes):
        ident=re.sub(r"[^A-Za-z0-9_]", "_", str(node.get("id",f"N{i}"))) or f"N{i}"
        label=str(node.get("label",ident)).replace('"', "'")
        lines.append(f'    {ident}["{label}"]')
    for edge in edges:
        a=re.sub(r"[^A-Za-z0-9_]", "_", str(edge.get("from","")))
        b=re.sub(r"[^A-Za-z0-9_]", "_", str(edge.get("to","")))
        if a and b: lines.append(f"    {a} --> {b}")
    return "\n".join(lines)


def _make_pptx(title, slides):
    prs=Presentation()
    prs.slide_width= Inches(13.333); prs.slide_height= Inches(7.5)
    blank=prs.slide_layouts[6]
    for idx, item in enumerate(slides):
        slide=prs.slides.add_slide(blank)
        bg=slide.background.fill; bg.solid(); bg.fore_color.rgb=RGBColor(35,31,32)
        # top accent
        shape=slide.shapes.add_shape(1, Inches(0), Inches(0), prs.slide_width, Inches(.16))
        shape.fill.solid(); shape.fill.fore_color.rgb=RGBColor(197,174,104); shape.line.fill.background()
        title_box=slide.shapes.add_textbox(Inches(.7), Inches(.55), Inches(12), Inches(1.0))
        p=title_box.text_frame.paragraphs[0]; p.text=str(item.get("title", f"{title} — {idx+1}")); p.font.size=Pt(28); p.font.bold=True; p.font.color.rgb=RGBColor(228,202,128)
        bullets=item.get("bullets",[])
        body=slide.shapes.add_textbox(Inches(.9), Inches(1.8), Inches(11.6), Inches(4.8))
        tf=body.text_frame; tf.word_wrap=True
        for j, bullet in enumerate(bullets[:7]):
            para=tf.paragraphs[0] if j==0 else tf.add_paragraph()
            para.text=str(bullet); para.level=0; para.font.size=Pt(21); para.font.color.rgb=RGBColor(245,242,234); para.space_after=Pt(14)
        footer=slide.shapes.add_textbox(Inches(.7), Inches(7.05), Inches(12), Inches(.25))
        fp=footer.text_frame.paragraphs[0]; fp.text=f"STUDIGENCE AI  •  {idx+1}"; fp.font.size=Pt(9); fp.font.color.rgb=RGBColor(197,174,104)
    buf=io.BytesIO(); prs.save(buf); return buf.getvalue()


def creative_studio(uid):
    _header()
    tabs=st.tabs(["Image → PDF","AI Diagram","PDF by Prompt","PPT by Prompt","Explain Notes Image"])
    with tabs[0]:
        st.subheader("Convert one or more images into a PDF")
        files=st.file_uploader("Choose images",type=["png","jpg","jpeg","webp","bmp"],accept_multiple_files=True,key="img_pdf")
        if files:
            if st.button("Convert images to PDF",type="primary",key="convert_img_pdf"):
                try:
                    pages=[]
                    for f in files:
                        im=Image.open(io.BytesIO(f.getvalue()))
                        im=ImageOps.exif_transpose(im).convert("RGB")
                        pages.append(im)
                    if pages:
                        out=io.BytesIO(); pages[0].save(out,format="PDF",save_all=True,append_images=pages[1:],resolution=150)
                        st.session_state["img_pdf_result"]=out.getvalue()
                        st.success(f"Created a {len(pages)}-page PDF.")
                except Exception as e: st.error(f"Image conversion failed: {e}")
        if st.session_state.get("img_pdf_result"):
            st.download_button("Download converted PDF",st.session_state["img_pdf_result"],file_name="studigence_images.pdf",mime="application/pdf",key="download_img_pdf")

    with tabs[1]:
        st.subheader("Find and draw a diagram for any study topic")
        topic=st.text_input("Topic",placeholder="e.g. Working of a neural network",key="diagram_topic")
        style=st.selectbox("Diagram style",["Flowchart","Process diagram","Concept map"],key="diagram_style")
        if st.button("Generate diagram",type="primary",key="diagram_make"):
            if not topic.strip(): st.warning("Enter a topic first.")
            else:
                prompt=f"""Create a correct educational {style.lower()} for: {topic}.
Return ONLY valid JSON with this exact shape:
{{"title":"short title","nodes":[{{"id":"A","label":"short step or concept"}}],"edges":[{{"from":"A","to":"B"}}]}}
Use 4 to 9 nodes, meaningful order, accurate relationships, short labels, and only IDs that exist. No markdown."""
                with st.spinner("Planning the diagram…"):
                    answer=_ai(prompt)
                data=_parse_json(answer)
                if data and isinstance(data.get("nodes"),list) and data["nodes"]:
                    nodes=data["nodes"][:9]; edges=data.get("edges",[])[:12]
                    try:
                        png=_diagram_png(data.get("title",topic),nodes,edges)
                        st.session_state["diagram_result"]=(png,_mermaid(nodes,edges),data.get("title",topic))
                    except Exception as e: st.error(f"Could not draw diagram: {e}")
                elif answer:
                    st.warning("The AI response was not valid diagram data. Try a more specific topic.")
        if st.session_state.get("diagram_result"):
            png,code,ttl=st.session_state["diagram_result"]
            st.image(png,caption=ttl,use_container_width=True)
            c1,c2=st.columns(2)
            c1.download_button("Download diagram PNG",png,file_name=_safe_filename(ttl)+".png",mime="image/png")
            c2.download_button("Download Mermaid source",code,file_name=_safe_filename(ttl)+".mmd",mime="text/plain")
            with st.expander("View editable Mermaid diagram source"): st.code(code,language="mermaid")

    with tabs[2]:
        st.subheader("Create a study PDF from a prompt")
        prompt=st.text_area("Describe the PDF you want",placeholder="Create detailed MCA notes on A* search with definition, algorithm, worked example, advantages, limitations and exam questions.",height=120,key="pdf_prompt")
        length=st.selectbox("Detail level",["Quick revision (1–2 pages)","Detailed notes (3–5 pages)","Exam preparation pack"],key="pdf_length")
        if st.button("Generate PDF",type="primary",key="prompt_pdf"):
            if not prompt.strip(): st.warning("Describe the PDF first.")
            else:
                with st.spinner("Writing your study document…"):
                    content=_ai(f"Write a well-structured, fact-conscious educational document. Detail level: {length}. User request: {prompt}. Use Markdown headings, bullet points, examples and a recap. Do not invent citations or claim unverified sources.")
                if content:
                    try:
                        st.session_state["prompt_pdf_result"]=_pdf_bytes(prompt[:90],content)
                        st.session_state["prompt_pdf_name"]=_safe_filename(prompt[:45])+".pdf"
                        st.success("Your PDF is ready.")
                    except Exception as e: st.error(f"PDF creation failed: {e}")
        if st.session_state.get("prompt_pdf_result"):
            st.download_button("Download generated PDF",st.session_state["prompt_pdf_result"],file_name=st.session_state["prompt_pdf_name"],mime="application/pdf")

    with tabs[3]:
        st.subheader("Generate a PowerPoint presentation from a prompt")
        prompt=st.text_area("Presentation topic and requirements",placeholder="Create an 8-slide MCA presentation on Machine Learning: intro, types, workflow, algorithms, applications, example, challenges and conclusion.",height=120,key="ppt_prompt")
        n=st.slider("Number of slides",4,15,8,key="ppt_slides")
        audience=st.selectbox("Audience",["School students","Undergraduate","MCA / University","Professional"],key="ppt_audience")
        if st.button("Generate PowerPoint",type="primary",key="prompt_ppt"):
            if not prompt.strip(): st.warning("Enter a presentation prompt.")
            else:
                ppt_prompt=f"""Create exactly {n} presentation slides for {audience}. Topic/request: {prompt}
Return ONLY valid JSON: {{"slides":[{{"title":"slide title","bullets":["bullet 1","bullet 2"]}}]}}
Each slide should have 2-5 concise bullets, logical flow, no invented citations, and an appropriate conclusion. No markdown."""
                with st.spinner("Designing your slides…"): answer=_ai(ppt_prompt)
                data=_parse_json(answer)
                if data and isinstance(data.get("slides"),list) and data["slides"]:
                    try:
                        ppt=_make_pptx(prompt[:70],data["slides"][:n])
                        st.session_state["ppt_result"]=ppt
                        st.success(f"PowerPoint ready with {min(n,len(data['slides']))} slides.")
                    except Exception as e: st.error(f"PowerPoint creation failed: {e}")
                elif answer: st.warning("The AI did not return valid slide data. Try again with a clearer prompt.")
        if st.session_state.get("ppt_result"):
            st.download_button("Download PowerPoint",st.session_state["ppt_result"],file_name="studigence_prompt_presentation.pptx",mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

    with tabs[4]:
        st.subheader("Upload a photo of notes, textbook pages or a handwritten diagram")
        st.caption("Robo uses image understanding to read the visible content. Clear, well-lit images work best.")
        image=st.file_uploader("Upload notes image",type=["png","jpg","jpeg","webp"],key="notes_image")
        mode=st.radio("How should Robo help?",["Explain in simpler words","Make it shorter for revision","Do both"],horizontal=True,key="notes_mode")
        if image and st.button("Read and explain image",type="primary",key="image_explain"):
            mime=image.type or "image/png"
            if mode=="Explain in simpler words":
                prompt="Read the study notes in this image carefully. Preserve technical terms and meaning. Explain each important point in simpler student-friendly language. If any text is unreadable, say so instead of guessing. Use headings and one simple example where useful."
            elif mode=="Make it shorter for revision":
                prompt="Read the study notes in this image and create concise revision notes. Keep definitions, formulas, key terms and essential steps. Do not omit critical conditions. Mark any unreadable text rather than guessing."
            else:
                prompt="Read the study notes in this image. First explain every important idea in simple student-friendly language, then provide a separate short revision version. Preserve technical accuracy and flag unreadable text."
            with st.spinner("Reading your notes…"):
                result=generate_with_image(prompt,image.getvalue(),mime)
            st.session_state["image_notes_result"]=result
        if st.session_state.get("image_notes_result"):
            st.markdown(st.session_state["image_notes_result"])
            st.download_button("Download explanation",st.session_state["image_notes_result"],file_name="studigence_image_notes.md",mime="text/markdown")

    st.caption("AI-created diagrams, notes, PDFs and slides should be checked against your course material before submission.")
