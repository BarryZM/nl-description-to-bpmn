# coding=utf-8
"""
Function for extracting actions from sentence
"""
from typing import List

from spacy.tokens.span import Span

import main.find_tokens_with_dependency as dep
from main.objects.action import Action
from main.objects.actor import Actor


def extract_svo_constructs(sentence: Span, actors: List[Actor]) -> List[Action]:
    tmp_output = []
    root = sentence.root
    nsubj_list = dep.find_tokens_with_dependencies_for_token_in_subtree(root, ["nsubj"])
    nsubjpass_list = dep.find_tokens_with_dependencies_for_token_in_subtree(root, ["nsubjpass"])
    if len(nsubj_list) > 0:
        for token in nsubj_list:
            output_obj = None
            subject = token
            verb = subject.head
            objects_list = dep.find_tokens_with_dependencies_for_token_in_subtree(verb, ["dobj", "iobj", "pobj", "attr"])
            for complement in objects_list:
                if complement.head == verb:
                    output_obj = complement
            action = Action(subject=subject, verb=verb, new_object=output_obj, position=verb.i)
            insert_flag = True
            if len(tmp_output) > 0:
                for tmp_action in tmp_output:
                    if action.get_subject() == tmp_action.get_subject() \
                            and action.get_verb() == tmp_action.get_verb() \
                            and action.get_object() == tmp_action.get_object():
                        insert_flag = False
                if insert_flag:
                    tmp_output.append(action)
            else:
                tmp_output.append(action)
    if len(nsubjpass_list) > 0:
        for token in nsubjpass_list:
            subject = token
            verb = subject.head
            action = Action(subject=subject, verb=verb, position=verb.i)
            action.set_passive(True)
            insert_flag = True
            if len(tmp_output) > 0:
                # Check if action wasn't already discovered
                for tmp_action in tmp_output:
                    if action.get_subject() == tmp_action.get_subject() \
                            and action.get_verb() == tmp_action.get_verb() \
                            and action.get_object() == tmp_action.get_object():
                        insert_flag = False
                if insert_flag:
                    tmp_output.append(action)
            else:
                tmp_output.append(action)
    extract_actions_from_conjunction(sentence, tmp_output)

    # Check if extracted action can be assigned to verified actor
    for action in tmp_output:
        for actor in actors:
            if actor.get_actor_token() == action.get_subject():
                action.set_actor(actor)
    return tmp_output


def extract_actions_from_conjunction(sentence: Span, tmp_output: List[Action]) -> List[Action]:
    for word in sentence:
        if word.dep_ == "conj":
            conj_verb = word
            output_object = None
            for child in conj_verb.children:
                if child.dep_ in ("dobj", "iobj", "pobj", "attr"):
                    output_object = child

            subject = None
            token = conj_verb
            while token is not None and subject is None:
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = child
                if token.dep_ == "ROOT":
                    break
                if subject is None:
                    token = token.head

            if subject is not None:
                action = Action(subject=subject, verb=conj_verb, new_object=output_object,position=conj_verb.i)
                if len(tmp_output) > 0:
                    insert_flag = True
                    for tmp_action in tmp_output:
                        if action.get_subject() == tmp_action.get_subject() \
                                and action.get_verb() == tmp_action.get_verb() \
                                and action.get_object() == tmp_action.get_object():
                            insert_flag = False
                    if insert_flag:
                        tmp_output.append(action)
                else:
                    tmp_output.append(action)