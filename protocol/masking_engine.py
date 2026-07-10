from protocol.masking import generate_mask
from protocol.context import MaskContext
from protocol.results import MaskResult
from protocol.masking_context import MaskingContext
from protocol.pairwise_mask import generate_pairwise_mask
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
            print("="*60)
            print("Shared Secret: ", context.shared_secret)
            print("Type: ", type(context.shared_secret))
            print("="*60)
            mask = generate_pairwise_mask(
                shared_secret=context.shared_secret,
                parameter=parameter,
                context=layer_context,
                my_node_id=context.my_node_id,
                peer_node_id=context.peer_node_id,
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