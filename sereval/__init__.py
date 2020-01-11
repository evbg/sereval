# -*- coding: utf-8 -*-
import traceback
from copy import deepcopy

__all__ = ['sereval']


def sereval(
    methods_list=(),
    break_if_error=False,
    recur_results=False,
    inject_last_method_result_to_kwargs=True,
    accumulate_results=True,
    return_kwargs=False,
    return_results_accumulator=False,
    return_results=True,
    show_params_in_results=False,
    show_results_with_error_only=False,
    _globals=None,
    **kwargs
):

    results = []
    results_accumulator = {}
    last_method = {}
    assert type(methods_list) in (list, tuple)
    for i, input_method_container in enumerate(methods_list):
        error = None
        assert type(input_method_container) is dict
        method_name = input_method_container.get('method', 'None')
        _kwargs = input_method_container.pop('params', {})
        try:
            try:
                op = _globals[method_name]
            except KeyError:
                op = eval(method_name)
            if inject_last_method_result_to_kwargs:
                _kwargs.update(last_method.get('result', {}))
            else:
                _kwargs['last_method'] = last_method
            if '_eval_params' in _kwargs:
                _eval_params = _kwargs['_eval_params']
                _evaluated = {}
                for k in _eval_params:
                    try:
                        _evaluated[k] = eval(_eval_params[k])
                    except Exception:
                        _evaluated[k] = None
                _kwargs.update(_evaluated)
            result = op(**_kwargs)
            if type(result) is not dict:
                result = {'{}_result'.format(method_name): result}
        except Exception:
            result = {}
            error = traceback.format_exc()
        assert type(result) is dict
        results_accumulator.update(result)
        if accumulate_results:
            result = deepcopy(results_accumulator)
        current_result = {'result': result, 'error': error, 'index': i}
        if show_params_in_results or (
            return_kwargs and inject_last_method_result_to_kwargs
        ):
            input_method_container['params'] = _kwargs
        current_result.update(input_method_container)
        results.append(current_result)
        if recur_results:
            last_method = current_result
        else:
            last_method = {
                'result': result,
                'error': error,
                'index': i,
                'method': method_name,
            }
        if error and break_if_error:
            break

    ret = {}
    if return_kwargs:
        ret.update({'kwargs': kwargs})
    if return_results:
        if show_results_with_error_only:
            results_with_error = [r for r in results if r.get('error', None)]
            if results_with_error:
                ret.update({'results': results_with_error})
        else:
            ret.update({'results': results})
    if return_results_accumulator:
        ret.update({'results_accumulator': results_accumulator})
    return ret
