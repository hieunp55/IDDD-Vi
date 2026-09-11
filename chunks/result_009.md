Tập trung vào Domain Layer (Tầng Miền), việc áp dụng DIP (Dependency Inversion Principle - Nguyên lý Đảo ngược Phụ thuộc) cho phép cả Domain và Infrastructure (Tầng Hạ tầng) đều phụ thuộc vào abstractions (các trừu tượng hóa/interface) được định nghĩa bởi mô hình miền. Vì Application Layer (Tầng Ứng dụng) là client (bên tiêu thụ dịch vụ) trực tiếp của Domain, nó phụ thuộc vào các interface của Domain và truy cập gián tiếp tới Repository (Kho lưu trữ - đối tượng trừu tượng hóa việc truy xuất tập hợp thực thể) cùng bất kỳ lớp triển khai kỹ thuật nào của Domain Service (Dịch vụ Miền) do Infrastructure cung cấp. Tầng này có thể sử dụng một trong vài cách thức để tiếp nhận các triển khai này, bao gồm Dependency Injection (Tiêm phụ thuộc), Service Factory (Nhà máy Dịch vụ), và Plug In (Trình cắm) [Fowler, P of EAA]. Các ví dụ xuyên suốt cuốn sách này sử dụng Dependency Injection được cung cấp bởi Spring Framework và đôi khi sử dụng Service Factory thông qua lớp DomainRegistry. Trên thực tế, DomainRegistry sử dụng Spring để tra cứu các tham chiếu tới các bean hiện thực hóa những interface được định nghĩa bởi mô hình miền, bao gồm cả các Repository và Domain Service.

Một điều rất thú vị là khi suy ngẫm về sức ảnh hưởng của DIP đối với kiến trúc này, chúng ta có thể kết luận rằng thực chất không còn bất kỳ tầng nào tồn tại nữa. Cả các mối bận tâm cấp cao lẫn cấp thấp đều chỉ phụ thuộc duy nhất vào abstractions, điều này dường như đã lật đổ hoàn toàn cấu trúc xếp tầng (stack). Sẽ ra sao nếu chúng ta thực sự nghĩ đến việc đảo ngược hoàn toàn kiến trúc này và bổ sung thêm một chút tính đối xứng? Tiếp theo, hãy cùng xem cơ chế đó hoạt động như thế nào.

## Hexagonal or Ports and Adapters

Với Hexagonal Architecture (Kiến trúc Lục giác) [^2], Alistair Cockburn đã hệ thống hóa một phong cách kiến trúc nhằm tạo ra tính đối xứng [Cockburn]. Nó thúc đẩy mục tiêu này bằng cách cho phép nhiều loại client khác nhau có thể tương tác với hệ thống trên một vị thế hoàn toàn bình đẳng. Cần thêm một client mới? Không thành vấn đề. Chỉ cần bổ sung một Adapter (Bộ chuyển đổi) để chuyển đổi dữ liệu đầu vào của bất kỳ client nào thành dạng mà API nội bộ của ứng dụng có thể hiểu được. Đồng thời, các cơ chế đầu ra (output mechanisms) được hệ thống sử dụng, chẳng hạn như giao diện đồ họa, lưu trữ dữ liệu (persistence), và truyền thông điệp (messaging), cũng có thể đa dạng và dễ dàng hoán đổi cho nhau. Điều đó hoàn toàn khả thi vì một Adapter được tạo ra để chuyển đổi kết quả xử lý của ứng dụng thành định dạng mà một cơ chế đầu ra cụ thể chấp nhận.

Khi chúng ta đi sâu thảo luận về nó, bạn có thể sẽ đồng tình rằng kiến trúc này mang trong mình tiềm năng trường tồn vượt thời gian.

[^2]: Chúng tôi gọi kiến trúc này bằng cái tên Hexagonal, mặc dù tên gọi của nó dường như đã được đổi thành Ports and Adapters (Cổng và Bộ chuyển đổi). Bất chấp sự thay đổi tên gọi này, cộng đồng vẫn quen gọi nó là Hexagonal. Onion Architecture (Kiến trúc Củ hành) cũng đã xuất hiện sau đó. Tuy nhiên, đối với nhiều người, có vẻ như Onion chỉ là một tên gọi thay thế (đáng tiếc) cho Hexagonal. Chúng ta có thể an tâm coi chúng là một và giữ nguyên định nghĩa của [Cockburn].

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000114_9d9a44c04b680402062c07664b07dd0dbc99efb0aa991087cb1167e0adf20b87.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000115_7aeeb3fe42f3824bf9eafb991c3f60e3fe5d47c23685941188ffb1edb44e9916.png)

Ngày nay, nhiều nhóm phát triển tuyên bố rằng họ đang sử dụng Layers Architecture nhưng thực chất lại đang dùng Hexagonal. Điều này một phần xuất phát từ số lượng dự án hiện đang áp dụng một dạng Dependency Injection nào đó. Không phải cứ dùng Dependency Injection là tự động biến thành Hexagonal. Chỉ là nó khuyến khích một cách thức tổ chức kiến trúc nghiêng một cách tự nhiên về phía phong cách Ports and Adapters. Dù trong trường hợp nào, một sự hiểu biết thấu đáo hơn sẽ làm sáng tỏ điểm này.

Chúng ta thường nghĩ nơi mà các client tương tác với hệ thống là "front end" (đầu trước). Tương tự, chúng ta coi nơi ứng dụng truy xuất dữ liệu đã lưu, lưu trữ dữ liệu mới, hoặc gửi kết quả đầu ra là "back end" (đầu sau). Nhưng Hexagonal thúc đẩy một cách nhìn nhận hoàn toàn khác về các khu vực của một hệ thống, như được minh họa trong Hình 4.4. Có hai khu vực chính: bên ngoài (the outside) và bên trong (the inside). Phía bên ngoài cho phép các client khác nhau gửi dữ liệu đầu vào, đồng thời cung cấp các cơ chế để truy xuất dữ liệu lưu trữ, ghi lại kết quả đầu ra của ứng dụng (ví dụ: cơ sở dữ liệu), hoặc gửi nó tới những nơi khác trên hành trình xử lý (ví dụ: hệ thống messaging).

Hình 4.4 Kiến trúc Hexagonal còn được biết đến với tên gọi Ports and Adapters. Có các Adapter cho từng loại thành phần bên ngoài. Phía bên ngoài tiếp cận phía bên trong thông qua API của ứng dụng.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000116_09e481e2ab5556af1310637d9e9ad5329794412fec5c8afb24701df9f9c4ccbd.png)

## Cowboy Logic

AJ: "Lũ ngựa của tôi chắc chắn rất thích cái chuồng hình lục giác mới của chúng. Nó cho chúng nhiều góc hơn để chạy trốn mỗi khi tôi vác yên ngựa bước vào."

> 💡 **Giải thích thêm:** Câu đùa "Cowboy Logic" mang tính ẩn dụ châm biếm: chuồng ngựa truyền thống thường là hình tròn để ngựa không có góc kẹt/chạy trốn khi người chăn ngựa muốn bắt chúng đeo yên. Khi làm chuồng hình lục giác (nhiều cạnh/góc), lũ ngựa lại có thêm chỗ trốn. Trong phần mềm, tác giả chơi chữ liên hệ tới việc hình lục giác mang lại nhiều "cạnh/góc" (Ports) độc lập giúp hệ thống bên trong dễ dàng tiếp nhận hoặc cô lập các kết nối bên ngoài mà không bị phụ thuộc cứng.  
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000117_c04bc509531bb24469148cabc32bca90a5cafecac212bada8fb94215dfc9b898.png)

Trong Hình 4.4, mỗi loại client có một Adapter riêng [Gamma et al.], có nhiệm vụ chuyển đổi các giao thức đầu vào thành định dạng tương thích với API của ứng dụng — tức là phía bên trong. Mỗi cạnh của hình lục giác đại diện cho một loại Port (Cổng) khác nhau, dành cho đầu vào hoặc đầu ra. Ba trong số các yêu cầu của client đến thông qua cùng một loại Port đầu vào (Adapter A, B, và C), và một yêu cầu sử dụng một loại Port khác biệt (Adapter D). Có thể ba yêu cầu kia sử dụng HTTP (trình duyệt, REST, SOAP, v.v.) còn yêu cầu kia sử dụng AMQP (Advanced Message Queuing Protocol - ví dụ: RabbitMQ). Không có một định nghĩa cứng nhắc nào về ý nghĩa của một Port, biến nó thành một khái niệm vô cùng linh hoạt. Bất kể các Port được phân chia theo cách nào, khi yêu cầu của client đến, Adapter tương ứng sẽ chuyển đổi đầu vào của chúng. Sau đó, nó gọi một thao tác trên ứng dụng hoặc gửi cho ứng dụng một event (sự kiện). Quyền kiểm soát nhờ đó được chuyển giao vào phía bên trong.

## We Probably Are Not Implementing the Ports Ourselves

Chúng ta thực tế thường không tự mình triển khai các Port. Hãy coi một Port giống như HTTP và Adapter là một Java Servlet hoặc một lớp được gắn annotation JAX-RS có nhiệm vụ nhận các lệnh gọi phương thức từ một container (JEE) hoặc framework (RESTEasy hoặc Jersey). Hoặc chúng ta có thể tạo một message listener (bộ lắng nghe thông điệp) cho NServiceBus hoặc RabbitMQ. Trong trường hợp đó, Port ít nhiều chính là cơ chế messaging, còn Adapter là message listener, bởi vì trách nhiệm của message listener là trích xuất dữ liệu từ message và chuyển dịch nó thành các tham số phù hợp để truyền vào API của Ứng dụng (client của mô hình miền).

## Design the Application Inside per Functional Requirements

Khi sử dụng Hexagonal, chúng ta thiết kế ứng dụng dựa trên các use cases (trường hợp sử dụng), chứ không dựa trên số lượng client được hỗ trợ. Bất kỳ số lượng và loại client nào cũng có thể gửi yêu cầu thông qua các Port khác nhau, nhưng mỗi Adapter đều ủy quyền xử lý vào ứng dụng thông qua cùng một API duy nhất.

Ứng dụng tiếp nhận các yêu cầu thông qua API công khai của nó. Ranh giới của ứng dụng, hay hình lục giác bên trong, cũng chính là ranh giới của use case (hoặc user story). Nói cách khác, chúng ta nên xây dựng các use cases dựa trên các yêu cầu chức năng của ứng dụng, chứ không phải dựa trên số lượng client đa dạng hay các cơ chế đầu ra. Khi ứng dụng nhận được một yêu cầu qua API của nó, nó sử dụng mô hình miền để đáp ứng tất cả các yêu cầu liên quan đến việc thực thi logic nghiệp vụ. Vì vậy, API của ứng dụng được công bố dưới dạng một tập hợp các Application Service. Ở đây một lần nữa, các Application Service là client trực tiếp của mô hình miền, tương tự như khi áp dụng mô hình Layers.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000118_48c7499ab813d5d063e6cd29dcb9bf9634c53b435bc7fd0d9607e4962d64d911.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000119_86511c15721d4fba06d3584619ee112ced3d56a2d157c485e7adda966a5ccdc5.png)

Đoạn mã sau đây đại diện cho một tài nguyên RESTful được công bố bằng cách sử dụng JAX-RS. Một yêu cầu đến thông qua Port đầu vào HTTP, và bộ xử lý đóng vai trò là một Adapter, ủy quyền xử lý cho một Application Service:

```java
@Path("/tenants/{tenantId}/products")
public class ProductResource extends Resource {
    private ProductService productService;
    ...
    @GET
    @Path("{productId}")
    @Produces({ "application/vnd.saasovation.projectovation+xml" })
    public Product getProduct(
            @PathParam("tenantId") String aTenantId,
            @PathParam("productId") String aProductId,
            @Context Request aRequest) {
        Product product = productService.product(aTenantId, aProductId);
        if (product == null) {
            throw new WebApplicationException(Response.Status.NOT_FOUND);
        }
        return product; // được tuần tự hóa sang XML bằng MessageBodyWriter
    }
    ...
}

```

Các annotation JAX-RS khác nhau cung cấp một phần đáng kể chức năng của Adapter, bằng việc phân tích đường dẫn tài nguyên và biến đổi các tham số của nó thành các thực thể String. Thực thể ProductService được tiêm vào (injected) và được yêu cầu này sử dụng để ủy quyền xử lý vào ứng dụng bên trong. Đối tượng Product được tuần tự hóa (serialized) sang XML và đặt vào trong một Response, sau đó được gửi ra ngoài thông qua Port đầu ra HTTP.

## JAX-RS Isn't the Focus Here

Đây chỉ là một cách để sử dụng ứng dụng và mô hình miền bên trong. Về bản chất, JAX-RS không phải là yếu tố quan trọng. Thay vào đó, chúng ta hoàn toàn có thể sử dụng Restfulie, hoặc tạo một máy chủ Node.js chạy module restify. Xa hơn nữa, các Adapter được thiết kế để xử lý đầu vào từ các Port khác cũng sẽ ủy quyền xử lý cho cùng một API đó, như bạn sẽ thấy.

Thế còn phía bên kia của ứng dụng, ở bên phải thì sao? Hãy coi các triển khai của Repository là các Adapter lưu trữ dữ liệu (persistence Adapters), cung cấp quyền truy cập vào các thực thể Aggregate đã lưu trước đó và lưu trữ các thực thể mới. Như được mô tả trong sơ đồ (các Adapter E, F, và G), chúng ta có thể có các triển khai Repository dành cho cơ sở dữ liệu quan hệ, document stores (kho lưu trữ tài liệu), distributed cache (bộ nhớ đệm phân tán), và các kho lưu trữ

## HEXAGONAL OR PORTS AND ADAPTERS

trong bộ nhớ (in-memory stores). Nếu ứng dụng gửi các thông điệp Domain Event (Sự kiện Miền) ra bên ngoài, nó sẽ sử dụng một Adapter khác (H) dành riêng cho messaging. Adapter gửi thông điệp đầu ra là mặt đối lập của Adapter đầu vào hỗ trợ AMQP, và do đó nó đi ra thông qua một Port khác với Port được dùng cho việc lưu trữ dữ liệu.

Một ưu điểm lớn của Hexagonal là các Adapter rất dễ phát triển để phục vụ mục đích kiểm thử. Toàn bộ ứng dụng và mô hình miền có thể được thiết kế và kiểm thử trước khi các client và cơ chế lưu trữ thực tế tồn tại. Các bài kiểm thử có thể được tạo ra để vận hành ProductService từ rất lâu trước khi có bất kỳ quyết định nào về việc hỗ trợ các Port HTTP/REST, SOAP hay messaging. Bất kỳ số lượng client thử nghiệm nào cũng có thể được phát triển trước khi các bản vẽ khung sườn (wireframes) của giao diện người dùng được hoàn thành. Rất lâu trước khi một cơ chế lưu trữ dữ liệu được lựa chọn cho dự án, các Repository chạy trên bộ nhớ có thể được áp dụng để giả lập việc lưu trữ nhằm phục vụ kiểm thử. Xem Repositories (Chương 12) để biết chi tiết về việc phát triển các bản triển khai in-memory. Tiến độ công việc đáng kể có thể đạt được trên phần lõi mà không cần đến sự trợ giúp của các thành phần kỹ thuật bổ trợ.

Nếu đang sử dụng mô hình Layers thuần túy, hãy cân nhắc những lợi thế của việc phá vỡ cấu trúc đó và phát triển dựa trên phong cách Ports and Adapters. Khi được thiết kế đúng đắn, hình lục giác bên trong — ứng dụng và mô hình miền — sẽ không bị rò rỉ ra các phần bên ngoài. Điều này thúc đẩy một ranh giới ứng dụng sạch sẽ ở bên trong, nơi các use cases được triển khai. Phía bên ngoài, bất kỳ số lượng Adapter client nào cũng có thể hỗ trợ vô số bài kiểm thử tự động cùng các client thực tế, cũng như các cơ chế lưu trữ, truyền thông điệp và các cơ chế đầu ra khác.

Khi các nhóm phát triển tại SaaSOvation cân nhắc những ưu điểm của việc sử dụng Hexagonal Architecture, họ đã quyết định chuyển dịch từ Layers sang. Việc đó thực ra không hề khó khăn. Nó chỉ đòi hỏi việc áp dụng một tư duy hơi khác một chút khi sử dụng Spring Framework quen thuộc.

Bởi vì Hexagonal Architecture rất đa năng, nó hoàn toàn có thể trở thành nền tảng nâng đỡ các kiến trúc khác mà hệ thống yêu cầu. Chẳng hạn, chúng ta có thể tích hợp Service-Oriented (Hướng Dịch vụ), REST, hoặc Event-Driven Architecture (Kiến trúc Hướng Sự kiện); áp dụng CQRS; sử dụng Data Fabric (Mạng lưới Dữ liệu) hoặc Grid-Based Distributed Cache (Bộ nhớ đệm phân tán dạng lưới); hoặc gắn thêm cơ chế xử lý song song và phân tán Map-Reduce, hầu hết những điều này sẽ được thảo luận ở phần sau của chương. Phong cách Hexagonal tạo nên nền tảng vững chắc để hỗ trợ bất kỳ và tất cả các lựa chọn kiến trúc bổ sung đó. Còn có những cách tiếp cận khác, nhưng trong phần còn lại của chương này, hãy mặc định rằng Ports and Adapters được sử dụng để hỗ trợ phát triển xung quanh từng chủ đề còn lại được thảo luận.

## Service-Oriented

Kiến trúc Hướng Dịch vụ (Service-Oriented Architecture), hay SOA, mang nhiều ý nghĩa khác nhau đối với từng người. Điều này có thể khiến các cuộc thảo luận về nó gặp đôi chút thách thức. Tốt nhất là nên cố gắng tìm kiếm một tiếng nói chung, hoặc ít nhất là xác định rõ cơ sở cho cuộc thảo luận này. Hãy xem xét một số nguyên lý của SOA do Thomas Erl định nghĩa [Erl]. Bên cạnh thực tế rằng các dịch vụ luôn có khả năng tương tác với nhau (interoperable), chúng còn sở hữu tám nguyên lý thiết kế được trình bày trong Bảng 4.1.

Bảng 4.1 Các Nguyên lý Thiết kế Dịch vụ

| Service Design Principle (Nguyên lý Thiết kế Dịch vụ) | Description (Mô tả) |
| --- | --- |
| 1. Service Contract (Hợp đồng Dịch vụ) | Các dịch vụ thể hiện mục đích và năng lực của mình thông qua một hợp đồng được quy định trong một hoặc nhiều tài liệu mô tả. |
| 2. Service Loose Coupling (Liên kết Lỏng Dịch vụ) | Các dịch vụ giảm thiểu sự phụ thuộc lẫn nhau và chỉ duy trì nhận thức tối thiểu về nhau. |
| 3. Service Abstraction (Tính Trừu tượng Dịch vụ) | Các dịch vụ chỉ công bố hợp đồng của mình và che giấu logic nội bộ khỏi các client. |
| 4. Service Reusability (Khả năng Tái sử dụng Dịch vụ) | Các dịch vụ có thể được tái sử dụng bởi các thành phần khác nhằm xây dựng nên các dịch vụ có độ hạt thô hơn (coarse-grained). |
| 5. Service Autonomy (Tính Tự trị Dịch vụ) | Các dịch vụ kiểm soát môi trường và tài nguyên cơ sở của chính mình để duy trì tính độc lập, giúp chúng giữ được tính nhất quán và độ tin cậy. |
| 6. Service Statelessness (Tính Phi trạng thái Dịch vụ) | Các dịch vụ chuyển giao trách nhiệm quản lý trạng thái sang phía bên tiêu thụ (consumer), miễn là điều này không xung đột với những gì được kiểm soát vì Tính Tự trị Dịch vụ. |
| 7. Service Discoverability (Khả năng Khám phá Dịch vụ) | Các dịch vụ được mô tả kèm theo siêu dữ liệu (metadata) để phục vụ việc khám phá và giúp Hợp đồng Dịch vụ của chúng được thấu hiểu, biến chúng thành các tài sản có thể (tái) sử dụng. |
| 8. Service Composability (Khả năng Hợp thành Dịch vụ) | Các dịch vụ có thể được hợp thành bên trong các dịch vụ có độ hạt thô hơn, bất kể quy mô và độ phức tạp của cấu trúc hợp thành mà chúng trực thuộc. |

Hình 4.5 Kiến trúc Hexagonal hỗ trợ SOA, với các dịch vụ REST, SOAP, và messaging

Chúng ta có thể kết hợp các nguyên lý này với Hexagonal Architecture, với ranh giới dịch vụ nằm ở góc ngoài cùng bên trái và mô hình miền nằm ở vị trí trung tâm. Kiến trúc cơ bản được trình bày trong Hình 4.5, nơi các bên tiêu thụ tiếp cận dịch vụ bằng REST, SOAP, và messaging. Lưu ý rằng một hệ thống dựa trên Hexagonal có thể hỗ trợ nhiều endpoint (điểm cuối) dịch vụ kỹ thuật. Điều này có ảnh hưởng trực tiếp đến cách DDD được áp dụng bên trong một kiến trúc SOA.

Vì quan điểm còn rất khác nhau về việc SOA thực chất là gì và nó mang lại giá trị gì, sẽ không có gì đáng ngạc nhiên nếu bạn không đồng tình với những gì được trình bày ở đây. Martin Fowler gọi tình huống này là "sự mơ hồ hướng dịch vụ" (service-oriented ambiguity) [Fowler, SOA]. Do đó, tôi sẽ không cố gắng làm sáng tỏ toàn bộ SOA ở đây. Tuy nhiên, tôi sẽ đưa ra một góc nhìn về cách thức DDD khớp nối vào tập hợp các ưu tiên được công bố trong Tuyên ngôn SOA (SOA Manifesto) [^3].

[^3]: Bản thân Tuyên ngôn SOA đã phải nhận khá nhiều chỉ trích tiêu cực, nhưng chúng ta vẫn có thể chắt lọc được một số giá trị từ nó.

Trước hết, việc xem xét các góc nhìn thực tế được bày tỏ bởi một trong những người đóng góp cho bản Tuyên ngôn [Tilkov, Manifesto] sẽ cung cấp một bối cảnh quan trọng. Bình luận về bản Tuyên ngôn, ông đưa chúng ta tiến gần hơn ít nhất một hoặc hai bước tới việc hiểu các dịch vụ SOA có thể là gì:

> [Bản Tuyên ngôn] cho tôi lựa chọn xem một dịch vụ như một tập hợp các interface SOAP/WSDL hoặc một tập hợp các tài nguyên RESTful. . . . Đây không phải là một nỗ lực nhằm đưa ra một định nghĩa — mà là một nỗ lực tìm kiếm xem đâu là những giá trị và nguyên lý mà tất cả chúng ta có thể cùng đồng thuận.

Những nhận định của Stefan rất đáng lưu tâm. Việc tìm thấy tiếng nói chung luôn có ích, và chúng ta có lẽ có thể đồng ý rằng một business service (dịch vụ nghiệp vụ) có thể được cung cấp bởi bất kỳ số lượng technical services (dịch vụ kỹ thuật) nào.

Các dịch vụ kỹ thuật có thể là các tài nguyên RESTful, các interface SOAP, hoặc các kiểu message. Dịch vụ nghiệp vụ nhấn mạnh vào chiến lược kinh doanh, một phương thức để kết nối kinh doanh và công nghệ lại với nhau. Tuy nhiên, việc định nghĩa một dịch vụ nghiệp vụ đơn lẻ không đồng nghĩa với việc định nghĩa một Subdomain (Phân vùng miền - Chương 2) hay một Bounded Context (Ngữ cảnh Ranh giới) duy nhất. Chắc chắn rằng khi chúng ta thực hiện đánh giá cả không gian bài toán (problem space) lẫn không gian giải pháp (solution space), chúng ta sẽ thấy rằng một dịch vụ nghiệp vụ bao gồm nhiều thành phần của mỗi không gian đó. Do đó, Hình 4.5 chỉ minh họa kiến trúc của một Bounded Context đơn lẻ, một ngữ cảnh có thể cung cấp một tập hợp các dịch vụ kỹ thuật được hiện thực hóa thông qua một số tài nguyên RESTful, interface SOAP, hoặc các kiểu message — vốn chỉ là một phần của dịch vụ nghiệp vụ tổng thể. Trong không gian giải pháp SOA, chúng ta kỳ vọng sẽ thấy nhiều Bounded Context, bất kể từng ngữ cảnh riêng lẻ có sử dụng Hexagonal Architecture hay một kiến trúc nào khác. Cả SOA lẫn DDD đều không cần phải chỉ định cụ thể từng tập hợp dịch vụ kỹ thuật phải được thiết kế và triển khai như thế nào, vì có rất nhiều phương án lựa chọn khác nhau.

Tuy nhiên, khi sử dụng DDD, mục tiêu của chúng ta là tạo ra một Bounded Context với một mô hình miền hoàn chỉnh và được định nghĩa rõ ràng về mặt ngôn ngữ. Như đã thảo luận trong Bounded Contexts (Chương 2), chúng ta không muốn kiến trúc chi phối quy mô của mô hình miền. Điều đó có thể xảy ra nếu một hoặc một vài endpoint dịch vụ kỹ thuật, chẳng hạn như một tài nguyên REST đơn lẻ, một interface SOAP đơn lẻ, hoặc một kiểu message hệ thống, bị lạm dụng để áp đặt quy mô của một Bounded Context. Làm như vậy sẽ ép hệ thống phải chia thành rất nhiều Bounded Context và mô hình miền siêu nhỏ, có thể mỗi mô hình chỉ bao gồm đúng một Entity (Thực thể - đối tượng có định danh duy nhất xuyên suốt vòng đời) đóng vai trò là Gốc (Root) của một Aggregate đơn lẻ, nhỏ bé. Điều này có thể dẫn đến hàng trăm Bounded Context thu nhỏ như vậy trong một doanh nghiệp duy nhất.

Mặc dù cách tiếp cận đó có thể được coi là có những lợi thế kỹ thuật nhất định, nó không nhất thiết hiện thực hóa được các mục tiêu của DDD chiến lược (strategic DDD). Nó đi ngược lại với việc xây dựng một miền sạch sẽ, được mô hình hóa tốt dựa trên một Ubiquitous Language (Ngôn ngữ Toàn diện - ngôn ngữ chung thống nhất giữa chuyên gia nghiệp vụ và đội ngũ phát triển - Chương 1) hoàn chỉnh và bao quát, thực chất làm phân mảnh Ngôn ngữ đó. Và theo Tuyên ngôn SOA, việc phân mảnh các Bounded Context một cách gượng ép không nhất thiết là tinh thần cốt lõi của SOA:

1. Giá trị kinh doanh quan trọng hơn chiến lược kỹ thuật
2. Mục tiêu chiến lược quan trọng hơn lợi ích cục bộ của dự án

Nếu chấp nhận những điều này như những giá trị đáng giá, chúng sẽ hoàn toàn tương thích với DDD chiến lược. Như đã giải thích trong Bounded Contexts (Chương 2), các động lực kiến trúc thành phần kỹ thuật ít quan trọng hơn khi tiến hành phân chia các mô hình.

Các nhóm phát triển của SaaSOvation đã phải học một bài học khó khăn nhưng quan trọng: lắng nghe các yếu tố dẫn dắt về mặt ngôn ngữ sẽ phù hợp hơn với DDD. Mỗi Bounded Context trong số ba ngữ cảnh của họ đều phản ánh các mục tiêu của SOA — cả về mặt kinh doanh lẫn trong các dịch vụ kỹ thuật.

Ba mô hình mẫu được thảo luận trong Bounded Contexts (Chương 2), Context Maps (Chương 3), và Integrating Bounded Contexts (Chương 13) lần lượt đại diện cho từng mô hình miền đơn lẻ được định nghĩa chặt chẽ về mặt ngôn ngữ. Mỗi mô hình miền được bao bọc bởi một tập hợp các dịch vụ mở triển khai một SOA nhằm đáp ứng các mục tiêu kinh doanh.

## Representational State Transfer-REST

## Contributed by Stefan Tilkov

REST đã trở thành một trong những buzzword (từ ngữ thông dụng thời thượng) kiến trúc được sử dụng — và lạm dụng — nhiều nhất trong vài năm qua. Như thường lệ, mỗi người lại nghĩ về những thứ khác nhau khi nhắc đến từ viết tắt này. Đối với một số người, REST có nghĩa là gửi XML qua kết nối HTTP mà không dùng SOAP; một số người lại đồng nhất nó với việc sử dụng HTTP và JSON; những người khác lại tin rằng để làm REST thì cần phải gửi các đối số của phương thức dưới dạng tham số truy vấn trên URI. Tất cả những cách diễn giải này đều sai lầm, nhưng may mắn thay — và hoàn toàn khác biệt với nhiều khái niệm khác như "components" (thành phần) hay "SOA" — chúng ta có một nguồn tài liệu chuẩn mực và có thẩm quyền giải thích rõ ràng ý nghĩa của REST: luận án tiến sĩ của Roy T. Fielding, người đã đặt ra thuật ngữ này và định nghĩa nó một cách vô cùng sáng tỏ.

## REST as an Architectural Style

Điều đầu tiên cần nắm bắt khi cố gắng hiểu thấu đáo về REST là khái niệm về phong cách kiến trúc (architectural styles). Một phong cách kiến trúc có vai trò đối với kiến trúc tương tự như một design pattern (mẫu thiết kế) đối với một thiết kế cụ thể. Nó là sự trừu tượng hóa những khía cạnh chung của các cách triển khai cụ thể khác nhau, cho phép thảo luận về những lợi ích liên quan của chúng mà không bị sa đà vào các chi tiết kỹ thuật. Có rất nhiều phong cách kiến trúc hệ thống phân tán khác nhau, bao gồm client-server và distributed objects (đối tượng phân tán). Một vài chương đầu trong luận án của Fielding giải thích một số phong cách trong số đó, bao gồm cả các ràng buộc (constraints) mà chúng bắt buộc phải có đối với một kiến trúc tuân thủ từng phong cách. Khái niệm về các phong cách kiến trúc và các ràng buộc do chúng áp đặt có thể khiến bạn cảm thấy hơi mang tính lý thuyết, và bạn nhận định hoàn toàn đúng. Chúng tạo nên nền tảng lý thuyết cho một phong cách kiến trúc (vào thời điểm đó là) hoàn toàn mới mà Fielding giới thiệu. Đó chính là REST — phong cách kiến trúc mà kiến trúc của Web được kỳ vọng sẽ tuân theo.

Tất nhiên, Web — vốn được định hình bởi các tiêu chuẩn quan trọng nhất của nó là URI, HTTP và HTML — đã ra đời trước công trình nghiên cứu tiến sĩ của Fielding. Nhưng ông từng là một trong những nhân tố chủ chốt trong việc chuẩn hóa HTTP 1.1, và có tầm ảnh hưởng to lớn đến nhiều quyết định thiết kế dẫn tới diện mạo của Web như chúng ta biết ngày nay [^4]. Nhìn theo góc độ này, REST là một phép ngoại suy lý thuyết (theoretical extrapolation), được tạo ra sau thực tế, đúc kết từ chính kiến trúc của Web.

Vậy tại sao hiện nay chúng ta lại đánh đồng "REST" với một cách thức xây dựng hệ thống cụ thể hoặc, thậm chí hạn hẹp hơn, là một cách để xây dựng Web services? Nguyên nhân của việc này, như thực tế cho thấy, là cũng giống như bất kỳ công nghệ nào khác, các giao thức Web có thể được sử dụng theo nhiều cách rất khác nhau. Một số cách phù hợp với mục tiêu của những nhà thiết kế ban đầu; một số cách thì không. Một phép loại suy thường được sử dụng làm nổi bật điều này là thông qua thế giới RDBMS (Hệ quản trị cơ sở dữ liệu quan hệ) vốn rất quen thuộc với nhiều người. Bạn có thể sử dụng một RDBMS đúng với các khái niệm kiến trúc của nó — tức là định nghĩa các bảng với các cột, quan hệ khóa ngoại, views, ràng buộc, v.v. — hoặc bạn có thể tạo một bảng duy nhất với hai cột, một cột tên là "key", một cột tên là "value", và chỉ đơn giản lưu trữ các đối tượng đã tuần tự hóa vào cột value đó. Đương nhiên, bạn vẫn đang sử dụng một RDBMS, nhưng rất nhiều lợi ích của nó sẽ không còn khả dụng cho bạn (các truy vấn có ý nghĩa, joins, sắp xếp và nhóm, v.v.).

Theo cách tương tự, các giao thức Web có thể được sử dụng phù hợp với những ý tưởng ban đầu đã tạo nên bản sắc của chúng — với một kiến trúc tuân thủ phong cách kiến trúc REST — hoặc được sử dụng theo cách phá vỡ phong cách này. Và tương tự như ví dụ về RDBMS của chúng ta, nếu phớt lờ phong cách kiến trúc nền tảng thì hậu quả sẽ do chính chúng ta gánh chịu. Do đó, một loại kiến trúc hệ thống phân tán khác có thể sẽ phù hợp hơn nếu cuối cùng chúng ta không khai thác được bất kỳ lợi ích nào từ việc sử dụng HTTP theo cách "RESTful", cũng tương tự như việc kho lưu trữ NoSQL/key-value là lựa chọn tốt hơn để lưu trữ toàn bộ giá trị gắn liền với một khóa duy nhất.

[^4]: Ông cũng tình cờ là tác giả của thư viện HTTP được sử dụng rộng rãi đầu tiên, một trong những nhà phát triển ban đầu của máy chủ Apache HTTP, và là người sáng lập Apache Software Foundation.

## Key Aspects of a RESTful HTTP Server

Vậy đâu là những khía cạnh cốt lõi của một kiến trúc phân tán sử dụng "RESTful HTTP"? Hãy cùng xem xét phía máy chủ (server) trước. Lưu ý rằng việc chúng ta đang nói về một máy chủ được sử dụng bởi con người qua trình duyệt Web (một "ứng dụng Web") hay được sử dụng bởi một agent (tác nhân) khác, chẳng hạn như một client được viết bằng ngôn ngữ lập trình tùy chọn của bạn (một "Web service"), là hoàn toàn không có sự khác biệt về bản chất.

Trước hết, đúng như tên gọi của nó, resources (tài nguyên) là một khái niệm then chốt. Như thế nào? Với tư cách là một nhà thiết kế hệ thống, bạn quyết định đâu là những "thực thể" (things) có ý nghĩa mà bạn muốn phơi bày để có thể truy cập từ bên ngoài, và bạn gán cho mỗi thực thể một định danh riêng biệt. Nhìn chung, mỗi tài nguyên có một URI, và quan trọng hơn, mỗi URI phải trỏ đến một tài nguyên duy nhất — những "thực thể" bạn phơi bày ra bên ngoài cần phải có khả năng định địa chỉ riêng lẻ (individually addressable). Ví dụ, bạn có thể quyết định rằng mỗi khách hàng, mỗi sản phẩm, mỗi danh sách sản phẩm, mỗi kết quả tìm kiếm, và có thể mỗi thay đổi đối với danh mục sản phẩm đều phải là các tài nguyên độc lập theo đúng nghĩa. Các tài nguyên có các representations (biểu diễn), là sự thể hiện trạng thái của chúng, dưới một hoặc nhiều định dạng. Chính thông qua các representation — một tài liệu XML hoặc JSON, dữ liệu gửi lên từ một biểu mẫu HTML, hoặc một định dạng nhị phân nào đó — mà các client tương tác với các tài nguyên.

Khía cạnh then chốt tiếp theo là ý tưởng về giao tiếp phi trạng thái (stateless communication), sử dụng các self-descriptive messages (thông điệp tự mô tả). Đó là một yêu cầu HTTP mang đầy đủ tất cả thông tin mà máy chủ cần để xử lý nó. Tất nhiên, máy chủ có thể (và thường sẽ) sử dụng trạng thái lưu trữ bền vững của chính nó để hỗ trợ, nhưng điều quan trọng là client và máy chủ không dựa vào từng yêu cầu riêng lẻ để thiết lập một ngữ cảnh ngầm định (một session - phiên làm việc). Điều này cho phép truy cập vào từng tài nguyên một cách độc lập với các yêu cầu khác, một khía cạnh giúp đạt được khả năng mở rộng quy mô khổng lồ.

Nếu bạn coi các tài nguyên như các đối tượng — và hoàn toàn hợp lý khi làm như vậy — thì việc đặt câu hỏi chúng nên có loại interface nào là hoàn toàn xác đáng. Câu trả lời chính là một khía cạnh rất quan trọng khác giúp phân biệt REST với bất kỳ phong cách kiến trúc hệ thống phân tán nào khác. Tập hợp các phương thức mà bạn có thể gọi là cố định. Mọi đối tượng đều hỗ trợ cùng một interface duy nhất. Trong RESTful HTTP, các phương thức chính là các động từ HTTP (HTTP verbs) — quan trọng nhất là GET, PUT, POST, DELETE — có thể được áp dụng lên các tài nguyên.

Mặc dù thoạt nhìn có vẻ giống, các phương thức này không hoàn toàn chuyển dịch tương đương sang các thao tác CRUD (Create, Read, Update, Delete). Việc tạo ra các tài nguyên không đại diện cho bất kỳ thực thể bền vững nào mà thay vào đó đóng gói hành vi được kích hoạt khi một động từ thích hợp được áp dụng lên chúng là điều rất phổ biến. Mỗi phương thức HTTP đều có một định nghĩa rất rõ ràng trong đặc tả kỹ thuật của HTTP. Ví dụ, phương thức GET chỉ được sử dụng cho các thao tác "an toàn" (safe operations): (1) nó không được thực hiện các hành động tạo ra tác động mà client có thể không yêu cầu; (2) nó luôn luôn chỉ đọc dữ liệu; (3) nó có tiềm năng được lưu vào bộ nhớ đệm (caching - nếu máy chủ chỉ định rõ điều này thông qua các tiêu đề phản hồi thích hợp).

Phương thức GET của HTTP đã được Don Box — một trong những nhân vật chủ chốt đứng sau các Web service kiểu SOAP — gọi là "phần hạ tầng đường ống hệ thống phân tán được tối ưu hóa tốt nhất trên thế giới". Lời nhận xét của ông nhấn mạnh rằng rất nhiều hiệu năng và khả năng mở rộng của Web mà chúng ta coi là hiển nhiên ngày nay có được là nhờ các tối ưu hóa của HTTP cho trường hợp sử dụng cụ thể, cực kỳ phổ biến này.

Một số phương thức HTTP có tính lũy đẳng (idempotent - thao tác thực thi nhiều lần vẫn mang lại kết quả trạng thái tương đương như một lần), nghĩa là chúng có thể được gọi lại một cách an toàn mà không gây ra sự cố trong trường hợp gặp lỗi hoặc kết quả không rõ ràng. Điều này đúng với GET, PUT, và DELETE.

Cuối cùng, một máy chủ RESTful cho phép client khám phá một lộ trình đi qua các bước chuyển đổi trạng thái khả dĩ của ứng dụng bằng phương tiện siêu phương tiện (hypermedia). Khái niệm này được gọi là HATEOAS (Hypermedia as the Engine of Application State - Siêu phương tiện như Động cơ Thúc đẩy Trạng thái Ứng dụng) trong luận án của Fielding. Nói một cách đơn giản hơn, các tài nguyên riêng lẻ không đứng độc lập một mình. Chúng được kết nối, liên kết với nhau. Điều này không có gì đáng ngạc nhiên. Rốt cuộc, đó chính là nguồn gốc tạo nên cái tên của Mạng lưới mạng (the Web). Đối với máy chủ, điều này có nghĩa là nó sẽ nhúng các liên kết vào trong câu trả lời của mình, cho phép client tương tác với các tài nguyên được kết nối liên quan.

## Key Aspects of a RESTful HTTP Client

Một RESTful HTTP client di chuyển từ tài nguyên này sang tài nguyên tiếp theo bằng cách lần theo các liên kết có trong biểu diễn của tài nguyên hoặc được chuyển hướng (redirected) đến các tài nguyên sau khi gửi dữ liệu lên máy chủ để xử lý. Máy chủ và client phối hợp với nhau để điều hướng hành vi phân tán của client một cách linh hoạt. Vì một URI chứa tất cả thông tin cần thiết để phân giải một địa chỉ — bao gồm cả tên máy chủ (host name) và cổng (port) — một client tuân theo nguyên tắc siêu phương tiện có thể sẽ tương tác với một tài nguyên được lưu trữ bởi một ứng dụng khác, một máy chủ khác, hoặc thậm chí là một công ty hoàn toàn khác.

Trong một cấu hình REST lý tưởng, client sẽ bắt đầu với một URI duy nhất đã biết từ trước và tiếp tục lần theo các bộ điều khiển siêu phương tiện (hypermedia controls) kể từ thời điểm đó trở đi. Đây chính xác là mô hình mà trình duyệt sử dụng khi hiển thị mã HTML, bao gồm các liên kết và biểu mẫu, cho người dùng. Sau đó, nó sử dụng đầu vào của người dùng để tương tác với vô số ứng dụng Web mà không cần có hiểu biết từ trước về giao diện hay cách triển khai của chúng.

Phải thừa nhận rằng trình duyệt không phải là một tác nhân tự chủ hoàn toàn. Nó cần con người đưa ra các quyết định thực tế. Nhưng một client bằng mã lập trình có thể áp dụng nhiều nguyên tắc tương tự, ngay cả khi một số logic được viết cứng (hard-coded). Nó sẽ lần theo các liên kết thay vì suy đoán các cấu trúc URI cụ thể, hoặc suy đoán việc đặt chung các tài nguyên trên cùng một máy chủ, đồng thời nó sẽ tận dụng sự hiểu biết của mình về một hoặc nhiều kiểu định dạng phương tiện (media types).

## REST and DDD

Dù rất hấp dẫn, việc phơi bày trực tiếp một mô hình miền qua RESTful HTTP là điều không nên làm. Cách tiếp cận này thường dẫn đến các giao diện hệ thống mong manh hơn mức cần thiết, vì mỗi thay đổi trong mô hình miền sẽ phản ánh trực tiếp vào giao diện hệ thống. Có hai cách tiếp cận thay thế để kết hợp DDD và RESTful HTTP.

Cách tiếp cận đầu tiên là tạo một Bounded Context riêng biệt cho tầng giao diện của hệ thống và sử dụng các chiến lược thích hợp để truy cập Core Domain thực tế từ mô hình giao diện của hệ thống. Đây có thể được coi là một cách tiếp cận kinh điển, vì nó nhìn nhận giao diện của hệ thống như một thể thống nhất gắn kết được phơi bày đơn giản bằng các trừu tượng hóa tài nguyên thay vì các dịch vụ hay giao diện từ xa.

Hãy xem xét một ví dụ cụ thể về cách tiếp cận này. Chúng ta xây dựng một hệ thống quản lý một nhóm làm việc, bao gồm các nhiệm vụ, lịch trình/cuộc hẹn, các nhóm con, và tất cả các quy trình cần thiết để xử lý chúng. Chúng ta sẽ thiết kế một mô hình miền thuần khiết, không bị vấy bẩn bởi các chi tiết hạ tầng, nắm bắt được Ubiquitous Language và triển khai business logic cần thiết. Để công bố một giao diện cho mô hình miền được xây dựng cẩn thận này, chúng ta cung cấp một giao diện từ xa dưới dạng một tập hợp các tài nguyên RESTful. Các tài nguyên này phản ánh các use cases mà client cần, điều này rất có thể khác biệt so với mô hình miền thuần khiết. Tuy nhiên, mỗi tài nguyên đều được tạo nên từ, chẳng hạn, một hoặc nhiều Aggregate thuộc về Core Domain.

Tất nhiên, chúng ta có thể chỉ cần sử dụng các đối tượng miền làm tham số cho các phương thức tài nguyên JAX-RS — giả sử `/:user/:task` sẽ ánh xạ tới một phương thức `getTask()` trả về một đối tượng `Task`. Điều đó dường như rất đơn giản, nhưng nó đi kèm với một vấn đề lớn. Bất kỳ thay đổi nào đối với cấu trúc của đối tượng `Task` sẽ ngay lập tức được phản ánh trong giao diện từ xa, có thể làm hỏng hàng loạt client, mặc dù chúng ta có thể chỉ thay đổi một thứ hoàn toàn không liên quan đến thế giới bên ngoài. Điều này không tốt chút nào.

Vì vậy, cách tiếp cận đầu tiên được ưu tiên hơn, đó là tách rời Core Domain khỏi mô hình giao diện của hệ thống. Làm như vậy cho phép chúng ta thực hiện các thay đổi đối với Core Domain và sau đó quyết định trong từng trường hợp cụ thể xem liệu thay đổi đó có nhất thiết phải phản ánh trong mô hình giao diện của hệ thống hay không, và nếu có, đâu là cách ánh xạ tốt nhất để sử dụng. Lưu ý rằng với cách tiếp cận này, các lớp được thiết kế cho mô hình giao diện hệ thống thường chịu sự dẫn dắt của các lớp trong Core Domain, nhưng chắc chắn chịu sự dẫn dắt trực tiếp của các use cases. Lưu ý: Ngay cả trong trường hợp này, chúng ta vẫn có thể định nghĩa một custom media type.

Một cách tiếp cận khác phù hợp hơn khi sự nhấn mạnh được đặt nhiều hơn vào các kiểu định dạng phương tiện tiêu chuẩn (standard media types). Nếu các media type cụ thể được phát triển nhằm hỗ trợ không chỉ một giao diện hệ thống đơn lẻ mà là một danh mục các tương tác client-server tương tự nhau, một mô hình miền có thể được tạo ra để đại diện cho từng media type tiêu chuẩn đó. Một mô hình miền như vậy thậm chí có thể được tái sử dụng xuyên suốt giữa các client và server, mặc dù một số người ủng hộ REST và SOA coi đây là một anti-pattern (mẫu đối nghịch - giải pháp phản tác dụng). Lưu ý: Cách tiếp cận như vậy về bản chất là một Shared Kernel (Hạt nhân Chia sẻ - Chương 3) hoặc Published Language (Ngôn ngữ Xuất bản - Chương 3) theo các thuật ngữ của DDD.

Điều này phản ánh một cách tiếp cận từ ngoài vào trong (outside-in) và mang tính xuyên suốt (crosscutting). Trong miền quản lý nhóm làm việc và nhiệm vụ đã đề cập trước đó, có rất nhiều định dạng phổ biến. Hãy lấy định dạng `ical` làm ví dụ. Đây là một định dạng chung có thể được sử dụng bởi nhiều ứng dụng khác nhau. Trong trường hợp này, chúng ta sẽ bắt đầu bằng việc chọn một media type (`ical`) và sau đó tạo một mô hình miền cho định dạng này. Mô hình này sau đó có thể được sử dụng bởi bất kỳ hệ thống nào cần hiểu định dạng này — ví dụ như ứng dụng máy chủ của chúng ta, nhưng cũng có thể là các hệ thống khác (chẳng hạn như một Android client). Đương nhiên, với cách tiếp cận này, một máy chủ có thể cần xử lý nhiều media type khác nhau, và cùng một media type có thể được sử dụng bởi nhiều máy chủ.

Việc lựa chọn cách tiếp cận nào trong hai cách tiếp cận này phụ thuộc phần lớn vào mục tiêu của nhà thiết kế hệ thống xét về khả năng tái sử dụng. Giải pháp càng mang tính chuyên biệt hóa cao thì cách tiếp cận đầu tiên càng chứng tỏ được tính hữu ích. Giải pháp càng mang tính hữu dụng phổ quát, với mức độ cực hạn là việc chuẩn hóa bởi một tổ chức tiêu chuẩn chính thức, thì việc đi theo cách tiếp cận thứ hai lấy media type làm trung tâm lại càng trở nên hợp lý.

## Why REST?

Theo kinh nghiệm của tôi, một hệ thống được thiết kế tuân thủ các nguyên lý REST sẽ hiện thực hóa được lời hứa về sự liên kết lỏng (loose coupling). Nhìn chung, việc thêm các tài nguyên mới và các liên kết trỏ đến chúng trong các biểu diễn tài nguyên hiện có là rất dễ dàng. Việc bổ sung hỗ trợ cho các định dạng mới khi cần cũng rất thuận tiện, dẫn đến một tập hợp các kết nối hệ thống ít bị đổ vỡ hơn nhiều. Một hệ thống dựa trên REST dễ hiểu hơn nhiều, vì nó được chia thành các phần nhỏ hơn — các tài nguyên — mỗi tài nguyên đều phơi bày một điểm nhập (entry point) có thể kiểm thử, gỡ lỗi và sử dụng hoàn toàn độc lập. Thiết kế của HTTP và sự trưởng thành của hệ thống công cụ hỗ trợ các tính năng như viết lại URI (URI rewriting) và bộ nhớ đệm khiến RESTful HTTP trở thành một lựa chọn tuyệt vời cho các kiến trúc đòi hỏi cả tính liên kết lỏng lẫn khả năng mở rộng quy mô cao.

## Command-Query Responsibility Segregation, or CQRS

Việc truy vấn từ các Repository tất cả dữ liệu mà người dùng cần xem có thể rất khó khăn. Điều này đặc biệt đúng khi thiết kế trải nghiệm người dùng (UX design) tạo ra các góc nhìn dữ liệu cắt ngang qua nhiều loại và nhiều thực thể Aggregate khác nhau. Miền nghiệp vụ của bạn càng tinh vi, tình huống này càng có xu hướng xuất hiện thường xuyên hơn.

Chỉ sử dụng Repository để giải quyết vấn đề này có thể đem lại kết quả không như mong muốn. Chúng ta có thể buộc các client phải sử dụng nhiều Repository để lấy về tất cả các thực thể Aggregate cần thiết, sau đó tự tổng hợp những gì cần thiết vào một DTO (Data Transfer Object - Đối tượng Truyền tải Dữ liệu) [Fowler, P of EAA]. Hoặc chúng ta có thể thiết kế các phương thức tìm kiếm chuyên biệt (finders) trên nhiều Repository khác nhau để gom dữ liệu rời rạc bằng một truy vấn duy nhất. Nếu những giải pháp này có vẻ không phù hợp, có lẽ chúng ta nên thỏa hiệp về mặt thiết kế trải nghiệm người dùng, làm cho các giao diện hiển thị bám sát một cách cứng nhắc vào ranh giới Aggregate của mô hình. Phần lớn mọi người đều đồng ý rằng về lâu dài, một giao diện người dùng máy móc và nghèo nàn sẽ không thể đáp ứng được nhu cầu.

Liệu có một cách hoàn toàn khác biệt để ánh xạ dữ liệu miền sang các giao diện hiển thị (views) không? Câu trả lời nằm ở mẫu kiến trúc mang cái tên kỳ lạ: CQRS (Command-Query Responsibility Segregation - Phân tách Trách nhiệm Lệnh và Truy vấn) [Dahan, CQRS; Nijof, CQRS]. Nó là kết quả của việc nâng tầm một nguyên lý thiết kế đối tượng (hoặc thành phần) nghiêm ngặt — CQS (Command-Query Separation - Phân tách Lệnh và Truy vấn) — lên thành một mẫu kiến trúc.

Nguyên lý này, do Bertrand Meyer đề xuất, khẳng định như sau:

> Mỗi phương thức chỉ nên là một command (lệnh) thực hiện một hành động, hoặc một query (truy vấn) trả về dữ liệu cho bên gọi, nhưng không được phép là cả hai. Nói cách khác, việc đặt một câu hỏi không được làm thay đổi câu trả lời. Một cách chặt chẽ hơn, các phương thức chỉ nên trả về một giá trị nếu chúng có tính minh bạch tham chiếu (referentially transparent) và do đó không gây ra bất kỳ tác dụng phụ nào (side effects). [Wikipedia, CQS]

Ở cấp độ đối tượng, điều này có nghĩa là:

1. Nếu một phương thức làm thay đổi trạng thái của đối tượng, nó là một command, và phương thức đó không được phép trả về giá trị. Trong Java và C#, phương thức đó phải được khai báo kiểu `void`.
2. Nếu một phương thức trả về một giá trị nào đó, nó là một query, và nó không được phép trực tiếp hay gián tiếp gây ra sự thay đổi trạng thái của đối tượng. Trong Java và C#, phương thức đó phải được khai báo với kiểu dữ liệu của giá trị mà nó trả về.

Đó là một chỉ dẫn khá trực diện, và có cả cơ sở lý thuyết lẫn thực tiễn vững chắc để tuân thủ nó. Tuy nhiên, với tư cách là một mẫu kiến trúc khi áp dụng DDD, tại sao và làm thế nào để ứng dụng nó?

Hãy hình dung một mô hình miền, chẳng hạn như một trong những mô hình được thảo luận trong Bounded Contexts (Chương 2). Chúng ta thường sẽ thấy các Aggregate sở hữu cả các phương thức command và query. Chúng ta cũng sẽ thấy các Repository có một số phương thức tìm kiếm lọc theo các thuộc tính nhất định. Với CQRS, chúng ta sẽ gạt bỏ những "điều bình thường" này và thiết kế một cách thức khác biệt để truy vấn dữ liệu hiển thị.

Bây giờ, hãy nghĩ đến việc tách biệt toàn bộ các trách nhiệm truy vấn thuần túy truyền thống trong một mô hình ra khỏi toàn bộ các trách nhiệm thực thi các lệnh thuần túy trên chính mô hình đó. Các Aggregate sẽ không có các phương thức truy vấn (getters), mà chỉ có các phương thức command. Các Repository sẽ được tinh giản chỉ còn một phương thức `add()` hoặc `save()` (hỗ trợ lưu cho cả việc tạo mới lẫn cập nhật) và duy nhất một phương thức truy vấn, chẳng hạn như `fromId()`. Phương thức truy vấn duy nhất này nhận vào định danh duy nhất của một Aggregate và trả về chính Aggregate đó. Một Repository sẽ không thể được sử dụng để tìm kiếm một Aggregate bằng bất kỳ phương thức nào khác, chẳng hạn như lọc theo một số thuộc tính bổ sung. Với tất cả những phần đó đã được loại bỏ khỏi mô hình truyền thống, chúng ta gọi nó là command model (mô hình lệnh/mô hình ghi). Chúng ta vẫn cần một cách để hiển thị dữ liệu cho người dùng. Để làm điều đó, chúng ta tạo ra một mô hình thứ hai, mô hình được tinh chỉnh tối ưu cho các truy vấn. Đó chính là query model (mô hình truy vấn/mô hình đọc).

## Isn't This Accidental Complexity?

Ấn tượng ban đầu của bạn có thể là phong cách được đề xuất này đòi hỏi quá nhiều công sức và chúng ta chỉ đơn thuần đang thay thế một tập hợp vấn đề này bằng một tập hợp vấn đề khác, đồng thời phải viết thêm rất nhiều mã nguồn để thực hiện nó.

Tuy nhiên, đừng vội vàng bác bỏ phong cách này. Trong một số trường hợp, độ phức tạp tăng thêm là hoàn toàn có thể biện minh được. Hãy nhớ rằng, CQRS được sinh ra để giải quyết một bài toán cụ thể về sự tinh vi của giao diện hiển thị, chứ không phải để gắn thêm vào như một phong cách thời thượng nhằm làm đẹp cho bản sơ yếu lý lịch (CV) của bạn.

> 💡 **Giải thích thêm:** "Accidental Complexity" (Độ phức tạp ngẫu sinh/bất tất) là khái niệm kinh điển do Fred Brooks đưa ra trong bài luận nổi tiếng "No Silver Bullet" (1986). Nó chỉ độ phức tạp phát sinh do cách chúng ta chọn công nghệ, công cụ, kiến trúc hoặc cách lập trình, trái ngược với "Essential Complexity" (Độ phức tạp bản thể) vốn là bản chất nội tại của bài toán nghiệp vụ. Tác giả lưu ý tránh đưa thêm độ phức tạp kỹ thuật không cần thiết nếu bài toán không thực sự yêu cầu.
> Nguồn tham khảo: [Brooks, F. P. - No Silver Bullet: Essence and Accidents of Software Engineering](https://www.google.com/search?q=http://www.cs.nott.ac.uk/~pszcah/G51ISS/Documents/NoSilverBullet.html)

## Known by Other Names

Lưu ý rằng một số khu vực/thành phần của CQRS có thể được biết đến bằng những tên gọi khác. Thành phần mà tôi gọi là query model còn được gọi là read model, và command model còn được gọi là write model.

Kết quả là, mô hình miền truyền thống sẽ được tách làm đôi. Command model được lưu trữ trong một kho dữ liệu và query model được lưu trữ trong một kho dữ liệu khác. Chúng ta có được một tập hợp các thành phần như trong Hình 4.6. Một số chi tiết bổ sung sẽ làm sáng tỏ mẫu này.

## Examining Areas of CQRS

Hãy cùng đi qua từng khu vực chính của mẫu kiến trúc này. Chúng ta có thể bắt đầu với client và phần hỗ trợ truy vấn, sau đó chuyển sang command model và cách thức cập nhật vào query model được thực hiện.

Hình 4.6 Với CQRS, các command từ client truyền đi một chiều tới command model. Các query được thực thi trên một nguồn dữ liệu riêng biệt được tối ưu hóa cho việc trình diễn và chuyển giao tới giao diện người dùng hoặc các báo cáo.

## Client and Query Processor

Client (ở ngoài cùng bên trái trong sơ đồ) có thể là một trình duyệt Web hoặc một giao diện người dùng desktop tùy biến. Nó sử dụng một tập hợp các query processor (bộ xử lý truy vấn) chạy trên máy chủ. Sơ đồ không biểu diễn sự phân chia tầng mang ý nghĩa kiến trúc giữa các bậc (tiers) trên (các) máy chủ. Bất kể có những tầng nào tồn tại, query processor đại diện cho một thành phần đơn giản chỉ biết cách thực thi các truy vấn cơ bản trên một cơ sở dữ liệu, chẳng hạn như một kho lưu trữ SQL.

Không hề có các tầng phức tạp ở đây. Thành phần này nhiều nhất chỉ chạy một truy vấn đối với cơ sở dữ liệu lưu trữ truy vấn và có thể tuần tự hóa kết quả truy vấn sang một định dạng nào đó để truyền tải (có thể là một DTO, nhưng cũng có thể không), nếu điều đó là cần thiết. Nếu client chạy Java hoặc C#, nó có thể truy vấn cơ sở dữ liệu một cách trực tiếp. Tuy nhiên, điều đó có thể đòi hỏi một lượng lớn giấy phép (licenses) kết nối máy khách cơ sở dữ liệu, mỗi kết nối một license. Việc sử dụng một query processor tận dụng kỹ thuật connection pooling (hồ bơi kết nối - cơ chế tái sử dụng các kết nối cơ sở dữ liệu có sẵn) là lựa chọn tối ưu nhất.

Nếu client có thể tiêu thụ trực tiếp một tập kết quả cơ sở dữ liệu (ví dụ: dạng JDBC result set), việc tuần tự hóa là không cần thiết nhưng vẫn có thể là điều đáng mong muốn tùy trường hợp. Có hai trường phái tư tưởng ở đây. Một trường phái khẳng định rằng sự đơn giản tột cùng đòi hỏi tập kết quả, hoặc một phép tuần tự hóa cơ bản tương thích đường truyền của nó (XML hoặc JSON), phải được tiêu thụ trực tiếp bởi client. Những người khác lại khẳng định rằng các DTO nên được tạo ra và client sẽ tiêu thụ các DTO đó. Đây có thể là vấn đề về mặt sở thích, nhưng chúng ta có thể đồng ý rằng bất cứ khi nào chúng ta thêm vào các DTO và các bộ lắp ráp DTO Assembler [Fowler, P of EAA], độ phức tạp sẽ gia tăng, và nếu không thực sự cần thiết, đây sẽ là accidental complexity. Mỗi nhóm phát triển sẽ tự xác định cách tiếp cận nào hoạt động tốt nhất cho dự án của họ.

## Query Model (or Read Model)

Query model là một mô hình dữ liệu phi chuẩn hóa (denormalized data model). Nó không nhằm mục đích cung cấp hành vi nghiệp vụ của miền, mà chỉ thuần túy cung cấp dữ liệu phục vụ hiển thị (và có thể là báo cáo). Nếu mô hình dữ liệu này là một cơ sở dữ liệu SQL, mỗi bảng sẽ lưu giữ dữ liệu cho một loại giao diện hiển thị (màn hình) client duy nhất. Bảng có thể có nhiều cột, thậm chí là một tập siêu tập hợp (superset) chứa tất cả các cột cần thiết cho bất kỳ giao diện hiển thị cụ thể nào. Các database table view (khung nhìn bảng dữ liệu) có thể được tạo ra từ các bảng, mỗi view được sử dụng như một tập hợp con logic của toàn bộ dữ liệu.

## Create Support for as Many Views as Needed

Điều đáng lưu ý là các view dựa trên CQRS có thể vừa có chi phí thấp vừa dễ dàng thay thế/vứt bỏ (cả trong quá trình phát triển lẫn khi bảo trì). Điều này đặc biệt đúng nếu bạn sử dụng một dạng Event Sourcing đơn giản (xem phần 'Event Sourcing' ở phần sau của chương và Phụ lục A) và lưu trữ tất cả các Event vào một kho lưu trữ bền vững, nơi chúng có thể được xuất bản lại bất kỳ lúc nào để tạo ra dữ liệu view bền vững mới. Nhờ làm như vậy, bất kỳ view đơn lẻ nào cũng có thể được viết lại từ đầu một cách độc lập hoặc toàn bộ query model có thể được chuyển đổi sang một công nghệ lưu trữ dữ liệu hoàn toàn khác. Điều này giúp dễ dàng tạo và duy trì các view liên tục đáp ứng các nhu cầu giao diện người dùng không ngừng thay đổi. Nó có thể dẫn đến những trải nghiệm người dùng trực quan hơn, thoát khỏi mô hình bảng dữ liệu truyền thống để trở nên phong phú hơn rất nhiều.

141

Ví dụ, một bảng có thể được thiết kế với đầy đủ dữ liệu để hiển thị giao diện người dùng cho người dùng thông thường, người quản lý, và quản trị viên. Nếu một database table view tương ứng được tạo ra cho từng loại người dùng đó, dữ liệu cho từng vai trò bảo mật sẽ được phân chia một cách thích hợp. Điều này tích hợp sẵn tính bảo mật vào dữ liệu hiển thị theo từng loại người dùng. Một thành phần giao diện của người dùng thông thường sẽ chọn tất cả các cột từ table view của người dùng thông thường. Một thành phần giao diện của người quản lý sẽ chọn tất cả các cột từ table view của người quản lý. Bằng cách đó, người dùng thông thường sẽ không thể nhìn thấy những gì mà người quản lý có thể thấy.

Lý tưởng nhất là một câu lệnh `SELECT` chỉ yêu cầu duy nhất một khóa chính (primary key) cho view đang được sử dụng. Tại đây, query processor chọn tất cả các cột từ table view dành cho người dùng thông thường của một sản phẩm:

```sql
SELECT * FROM vw_usr_product WHERE id = ?

```

Như một lưu ý bên lề, quy ước đặt tên table view được thấy ở đây không nhất thiết là một khuyến nghị chuẩn mực. Nó chỉ nhằm làm sáng tỏ thao tác mà câu lệnh `SELECT` mẫu đang thực hiện. Khóa chính tương ứng với định danh duy nhất của một loại Aggregate nào đó hoặc một tập hợp kết hợp của nhiều loại Aggregate được hợp nhất vào một bảng duy nhất. Trong ví dụ này, cột khóa chính `id` là định danh duy nhất của một Product trong command model. Thiết kế mô hình dữ liệu nên tuân theo, càng nhiều càng tốt, mẫu hình một bảng cho mỗi loại giao diện người dùng, với số lượng table view cần thiết để phản ánh các vai trò bảo mật của ứng dụng. Tuy nhiên, hãy giữ vững tính thực tế.

## Be Practical

Nếu có 25 nhà giao dịch tại một bàn giao dịch tần suất cao (high-frequency trading desk) và mỗi người đang giao dịch các loại chứng khoán mà hầu hết những người khác không được phép xem do các quy định tuân thủ của SEC (Ủy ban Chứng khoán và Giao dịch Hoa Kỳ), liệu chúng ta có cần đến 25 table view không? Việc sử dụng một bộ lọc theo nhà giao dịch (trader filter) sẽ phù hợp hơn nhiều. Nếu không, số lượng view cần bảo trì sẽ trở nên quá nhiều để có thể duy trì tính thực tiễn.

Trong thực tế, điều này có thể khó đạt được, và các truy vấn có thể phải thực hiện kết nối (join) nhiều bảng hoặc nhiều table view khi cần thiết cho mục đích sử dụng thực tế. Việc join giữa các view/bảng có thể là cần thiết hoặc ít nhất là thực tế hơn để đạt được sự lọc dữ liệu mong muốn. Điều này có xu hướng xảy ra, đặc biệt là khi có rất nhiều vai trò người dùng cùng tham gia hoạt động trong miền của bạn.

## Don't Database Table Views Cause Overhead?

Một database table view cơ bản không gây ra chi phí phụ trội (overhead) khi thực hiện các thao tác cập nhật trên bảng dữ liệu bên dưới. View đó chỉ đơn thuần tương ứng với một truy vấn, mà trong trường hợp này thậm chí còn không yêu cầu lệnh join. Chỉ có materialized views (khung nhìn cụ thể hóa - view lưu trữ sẵn kết quả dữ liệu trên đĩa) mới phải gánh chịu overhead khi cập nhật vì dữ liệu của view phải được sao chép vào một nơi riêng biệt để sẵn sàng cho các lệnh `SELECT`. Hãy cẩn trọng khi thiết kế các bảng và view để việc cập nhật query model đạt hiệu năng tối ưu.

## Client Drives Command Processing

Các client giao diện người dùng gửi các command tới máy chủ (hoặc thực thi gián tiếp một phương thức của Application Service) như một phương tiện để kích hoạt hành vi trên các Aggregate cư trú trong command model. Command được gửi đi chứa tên của hành vi cần thực thi và các tham số cần thiết để thực hiện hành vi đó. Gói dữ liệu command thực chất là một lệnh gọi phương thức đã được tuần tự hóa. Vì command model sở hữu các contract (hợp đồng giao diện) và hành vi được thiết kế cẩn trọng, việc đối chiếu các command với các contract là một phép ánh xạ rất trực diện.

Để hoàn thành điều này, giao diện người dùng phải thu thập đầy đủ dữ liệu cần thiết để truyền tham số chính xác cho command. Điều này hàm ý rằng thiết kế trải nghiệm người dùng phải được đầu tư suy nghĩ rất nhiều. Nó phải dẫn dắt người dùng hướng tới mục tiêu chuẩn xác là gửi đi một command tường minh. Một thiết kế giao diện người dùng mang tính quy nạp, hướng tác vụ (inductive, task-driven UI) sẽ phát huy hiệu quả tốt nhất [Inductive UI]. Nó lọc bỏ tất cả các tùy chọn không thích hợp, tập trung vào việc thực thi command một cách chuẩn xác. Dẫu vậy, việc thiết kế một giao diện người dùng mang tính diễn dịch (deductive UI) có khả năng sinh ra một command tường minh vẫn hoàn toàn khả thi.

## Command Processors

Một command khi gửi lên sẽ được tiếp nhận bởi một Command Handler/processor (bộ xử lý/điều phối lệnh), thành phần này có thể có một vài phong cách thiết kế khác nhau. Chúng ta sẽ xem xét các phong cách đó ở đây, cùng với một số ưu điểm và nhược điểm.

Chúng ta có thể sử dụng một phong cách phân loại (categorized style) với nhiều Command Handler nằm trong một Application Service duy nhất. Phong cách này tạo ra một interface và bản triển khai của Application Service cho một nhóm danh mục các command. Mỗi Application Service có thể có nhiều phương thức, mỗi phương thức được khai báo cho một loại command kèm theo các tham số phù hợp với danh mục đó. Ưu điểm hàng đầu ở đây là tính đơn giản. Loại handler này rất dễ hiểu, dễ tạo và dễ bảo trì.

Chúng ta có thể tạo ra một handler theo phong cách chuyên biệt (dedicated style). Mỗi handler sẽ là một lớp đơn lẻ chỉ có duy nhất một phương thức. Hợp đồng của phương thức sẽ phục vụ một command cụ thể kèm các tham số. Cách này có những ưu điểm rõ rệt: Mỗi handler/processor chỉ đảm nhận một trách nhiệm duy nhất (single responsibility); mỗi handler có thể được triển khai lại (redeploy) độc lập với những handler khác; các loại handler có thể được mở rộng quy mô độc lập (scale out) để xử lý khối lượng lớn các loại command nhất định.

Điều này dẫn tới phong cách hướng thông điệp (messaging style) của Command Handler. Mỗi command được gửi đi như một thông điệp bất đồng bộ và được chuyển phát tới một handler được thiết kế theo phong cách chuyên biệt. Điều này không chỉ cho phép mỗi thành phần xử lý lệnh nhận được các thông điệp có kiểu định danh cụ thể, mà các bộ xử lý của một loại nhất định còn có thể được bổ sung thêm để giải quyết tải xử lý command. Cách tiếp cận này không nên được sử dụng làm mặc định, vì nó có thiết kế phức tạp hơn. Thay vào đó, hãy bắt đầu bằng một trong hai phong cách kia dưới dạng các bộ xử lý command đồng bộ. Chỉ chuyển sang bất đồng bộ khi các yêu cầu về khả năng mở rộng quy mô thực sự đòi hỏi. Dẫu vậy, một số người sẽ đi đến kết luận rằng cách tiếp cận bất đồng bộ cung cấp sự tách rời về mặt thời gian (temporal decoupling) sẽ dẫn đến các hệ thống có khả năng phục hồi tốt hơn. Góc nhìn đó thường sẽ dẫn tới xu hướng ưu tiên triển khai các Command Handler theo phong cách messaging.

Bất kể loại handler nào được sử dụng, hãy tách rời từng handler khỏi tất cả các handler khác. Không cho phép bất kỳ handler nào phụ thuộc vào (sử dụng) bất kỳ handler nào khác. Điều này sẽ cho phép bất kỳ loại handler nào cũng có thể được triển khai lại một cách độc lập mà không gây ảnh hưởng đến các handler khác.

Các Command Handler nhìn chung chỉ thực hiện một vài công việc. Nếu một handler có khía cạnh khởi tạo, nó sẽ khởi tạo một thực thể Aggregate mới và thêm thực thể mới đó vào Repository của nó. Thông thường nhất, nó sẽ lấy một thực thể Aggregate từ Repository của nó và thực thi một hành vi phương thức command trên thực thể đó:

```java
@Transactional
public void commitBacklogItemToSprint(
        String aTenantId,
        String aBacklogItemId,
        String aSprintId) {
    TenantId tenantId = new TenantId(aTenantId);
    BacklogItem backlogItem = backlogItemRepository.backlogItemOfId(
            tenantId,
            new BacklogItemId(aBacklogItemId));
    Sprint sprint = sprintRepository.sprintOfId(
            tenantId,
            new SprintId(aSprintId));
    backlogItem.commitTo(sprint);
}

```
