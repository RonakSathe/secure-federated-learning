from protocol.masking import generate_mask
from protocol.context import MaskContext
from protocol.results import MaskResult
class MaskingEngine:
    def mask_parameters(self,parameters,shared_secret,session_id,round_number,session_salt):
        results = []
        for layer_id, parameter in enumerate(parameters):
            context = MaskContext(
                session_id=session_id,
                round_number=round_number,
                layer_id=layer_id,
                salt=session_salt,
            )
            mask = generate_mask(
                shared_secret=shared_secret,
                parameter=parameter,
                context=context,
                )
            result = MaskResult(
                layer_id=layer_id,
                original=parameter,
                mask=mask,
                masked=parameter+mask
            )
            results.append(result)

        return results