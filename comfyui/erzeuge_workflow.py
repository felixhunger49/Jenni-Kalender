#!/usr/bin/env python3
"""Erzeugt den ComfyUI-Workflow fuer die 7 Tierportraets (UI- und API-Format).

Aufruf: python3 comfyui/erzeuge_workflow.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CKPT = 'sd_xl_base_1.0.safetensors'
SEED = 20261201
STEPS, CFG, SAMPLER, SCHED = 30, 6.0, 'dpmpp_2m', 'karras'
SIZE = 1024

STYLE = ('soft watercolor children\'s book illustration, cute and friendly, big round eyes, rosy cheeks, '
         'muted pastel palette of sage green, dusty pink, cream and warm beige, gentle shading, '
         'head and shoulders portrait, centered, facing the viewer, plain light cream background, '
         'no background objects, christmas mood, high quality')

NEGATIVE = ('text, letters, watermark, signature, logo, frame, border, window, multiple animals, full body, '
            'photo, photorealistic, 3d render, dark, scary, angry, deformed, extra eyes, extra ears, '
            'cropped head, busy background, saturated neon colors, blurry')

ANIMALS = [
    ('fuchs', 'a cute baby fox with orange fur and white cheeks, wearing a sage green knitted beanie with a cream pompom and a dusty blue knitted scarf'),
    ('loewe', 'a cute lion cub with a fluffy golden-brown mane, wearing a terracotta knitted scarf'),
    ('baer', 'a cute brown teddy bear cub, wearing a dusty blue knitted beanie with a cream pompom and a dusty blue knitted scarf'),
    ('hase', 'a cute grey-beige bunny with long ears with pink inner ears, wearing a sage green knitted scarf'),
    ('pinguin', 'a cute baby penguin chick with a white face and orange beak, wearing a terracotta knitted beanie with a cream pompom and a dusty pink scarf'),
    ('otter', 'a cute baby otter with brown fur and a light muzzle, wearing a sage green knitted beanie with a cream pompom and a caramel knitted scarf'),
    ('giraffe', 'a cute baby giraffe with small ossicones and soft spots, wearing a dusty blue knitted scarf'),
]


def build():
    nodes, links = [], []
    nid = [0]
    lid = [0]

    def node(typ, pos, size, widgets, inputs=(), outputs=(), title=None):
        nid[0] += 1
        n = dict(id=nid[0], type=typ, pos=list(pos), size=list(size), flags={}, order=nid[0] - 1, mode=0,
                 inputs=[dict(name=nm, type=t, link=None) for nm, t in inputs],
                 outputs=[dict(name=nm, type=t, links=[], slot_index=i) for i, (nm, t) in enumerate(outputs)],
                 properties={'Node name for S&R': typ}, widgets_values=list(widgets))
        if title:
            n['title'] = title
        nodes.append(n)
        return n

    def link(a, aslot, b, bslot):
        lid[0] += 1
        t = a['outputs'][aslot]['type']
        links.append([lid[0], a['id'], aslot, b['id'], bslot, t])
        a['outputs'][aslot]['links'].append(lid[0])
        b['inputs'][bslot]['link'] = lid[0]

    ckpt = node('CheckpointLoaderSimple', (40, 300), (320, 100), [CKPT],
                outputs=[('MODEL', 'MODEL'), ('CLIP', 'CLIP'), ('VAE', 'VAE')], title='Modell (SDXL)')
    neg = node('CLIPTextEncode', (40, 480), (320, 180), [NEGATIVE], inputs=[('clip', 'CLIP')],
               outputs=[('CONDITIONING', 'CONDITIONING')], title='Negativ-Prompt (für alle Tiere)')
    link(ckpt, 1, neg, 0)
    lat = node('EmptyLatentImage', (40, 720), (320, 110), [SIZE, SIZE, 1], outputs=[('LATENT', 'LATENT')],
               title='Bildgröße')

    api = {
        '1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': CKPT}},
        '2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': NEGATIVE, 'clip': ['1', 1]}},
        '3': {'class_type': 'EmptyLatentImage', 'inputs': {'width': SIZE, 'height': SIZE, 'batch_size': 1}},
    }
    for i, (key, desc) in enumerate(ANIMALS):
        y = 40 + i * 330
        pos = node('CLIPTextEncode', (420, y), (420, 200), ['%s, %s' % (desc, STYLE)], inputs=[('clip', 'CLIP')],
                   outputs=[('CONDITIONING', 'CONDITIONING')], title='Prompt: %s' % key)
        ks = node('KSampler', (880, y), (300, 262), [SEED + i, 'fixed', STEPS, CFG, SAMPLER, SCHED, 1.0],
                  inputs=[('model', 'MODEL'), ('positive', 'CONDITIONING'), ('negative', 'CONDITIONING'),
                          ('latent_image', 'LATENT')], outputs=[('LATENT', 'LATENT')])
        dec = node('VAEDecode', (1220, y), (200, 50), [], inputs=[('samples', 'LATENT'), ('vae', 'VAE')],
                   outputs=[('IMAGE', 'IMAGE')])
        save = node('SaveImage', (1460, y), (300, 300), ['tier_%s' % key], inputs=[('images', 'IMAGE')],
                    title='Speichern: tier_%s' % key)
        link(ckpt, 1, pos, 0)
        link(ckpt, 0, ks, 0)
        link(pos, 0, ks, 1)
        link(neg, 0, ks, 2)
        link(lat, 0, ks, 3)
        link(ks, 0, dec, 0)
        link(ckpt, 2, dec, 1)
        link(dec, 0, save, 0)
        b = 10 + i * 10
        api[str(b)] = {'class_type': 'CLIPTextEncode', 'inputs': {'text': '%s, %s' % (desc, STYLE), 'clip': ['1', 1]}}
        api[str(b + 1)] = {'class_type': 'KSampler', 'inputs': {
            'seed': SEED + i, 'steps': STEPS, 'cfg': CFG, 'sampler_name': SAMPLER, 'scheduler': SCHED, 'denoise': 1.0,
            'model': ['1', 0], 'positive': [str(b), 0], 'negative': ['2', 0], 'latent_image': ['3', 0]}}
        api[str(b + 2)] = {'class_type': 'VAEDecode', 'inputs': {'samples': [str(b + 1), 0], 'vae': ['1', 2]}}
        api[str(b + 3)] = {'class_type': 'SaveImage', 'inputs': {'filename_prefix': 'tier_%s' % key, 'images': [str(b + 2), 0]}}

    ui = dict(last_node_id=nid[0], last_link_id=lid[0], nodes=nodes, links=links, groups=[], config={},
              extra={'ds': {'scale': 0.6, 'offset': [0, 0]}}, version=0.4)
    json.dump(ui, open(os.path.join(HERE, 'tierportraets_workflow.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(api, open(os.path.join(HERE, 'tierportraets_api.json'), 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    build()
