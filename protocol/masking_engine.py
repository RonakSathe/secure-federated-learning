from protocol.masking import generate_mask
from protocol.context import MaskContext
from protocol.results import MaskResult
from protocol.masking_context import MaskingContext
class MaskingEngine:
    def mask_parameters(self,parameters,context:MaskingContext):
        results = []
        for layer_id, parameter in enumerate(parameters):
            layer_context = MaskContext(
                session_id=context.session_id,
                round_number=context.round_number,
                layer_id=layer_id,
                salt=context.session_salt,
            )
            mask = generate_mask(
                shared_secret=context.shared_secret,
                parameter=parameter,
                context=layer_context,
                )
            result = MaskResult(
                layer_id=layer_id,
                original=parameter,
                mask=mask,
                masked=parameter+mask,
                context=layer_context,
            )
            results.append(result)

        return results